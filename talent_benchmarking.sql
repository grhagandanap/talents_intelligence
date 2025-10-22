-- config the vacnacy job as the input
WITH vacancy_config AS (
  SELECT 
    role_name, 
    job_level, 
    role_purpose, 
    selected_talent_ids AS benchmark_ids,
    COALESCE(
      weights_config,
      jsonb_build_object(
        'Motivation & Drive', 0.125,
        'Leadership & Influence', 0.125,
        'Cultural & Values Urgency', 0.125,
        'Creativity & Innovation Orientation', 0.125,
        'Cognitive Complexity & Problem-Solving', 0.125,
        'Social Orientation & Collaboration', 0.125,
        'Adaptability & Stress Tolerance', 0.125,
        'Conscientiousness & Reliability', 0.125
      )
    ) AS tgv_weights
  FROM talent_benchmarks 
  WHERE job_vacancy_id = 3
),
-- choosing benchmark talent/talents
benchmark_employees AS (
  SELECT DISTINCT e.employee_id, e.fullname
  FROM vacancy_config vc
  CROSS JOIN LATERAL unnest(vc.benchmark_ids) AS benchmark(employee_id)
  JOIN employees e ON e.employee_id = benchmark.employee_id
  JOIN performance_yearly p ON p.employee_id = e.employee_id AND p.rating = 5
),
-- joining the numeric type of psycohmetric TV
base_numeric AS (
  SELECT
    e.employee_id,
    tv.tv_id,
    tv.tv_name,
    tv.sub_tv_name,
    tv.tgv_name,
    CASE tv.tv_name
      WHEN 'Pauli' THEN e.pauli
      WHEN 'IQ' THEN e.iq
      WHEN 'GTQ' THEN e.gtq
      WHEN 'TIKI' THEN e.tiki
    END AS score,
    'numeric' AS score_type
  FROM profiles_psych e
  JOIN benchmark_employees b ON e.employee_id = b.employee_id
  JOIN tv_tgv_names tv ON tv.tv_name IN ('Pauli', 'IQ', 'GTQ', 'TIKI')
),
-- flatten the papi score
papi_flat AS (
  SELECT
    p.employee_id,
    tv.tv_id,
    tv.tv_name,
    tv.sub_tv_name,
    tv.tgv_name,
    p.score::numeric AS score,
    'numeric' AS score_type
  FROM papi_scores p
  JOIN benchmark_employees b ON p.employee_id = b.employee_id 
  JOIN tv_tgv_names tv
    ON tv.sub_tv_name = p.scale_code
   AND tv.tv_name = 'PAPI Kostick'
),
-- concat vertically for two tables above
all_scores AS (
  SELECT * FROM base_numeric
  UNION ALL
  SELECT * FROM papi_flat
),
--  calculate the baseline score 
baseline_score AS (
  SELECT
    tv_id,
    tv_name,
    sub_tv_name,
    tgv_name,
    score_type,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score::numeric) AS baseline_score
  FROM all_scores
  GROUP BY tv_id, tv_name, sub_tv_name, tgv_name, score_type
),
-- join the categorical TV
final_baseline AS (
  SELECT 
    t.tv_id,
    t.tv_name,
    t.sub_tv_name,
    t.tgv_name,
    COALESCE(b.score_type, 'categorical') AS score_type,
    COALESCE(b.baseline_score::text, t.sub_tv_name) AS baseline_score
  FROM tv_tgv_names t
  LEFT JOIN baseline_score b USING (tv_id)
),
-- calculate the comparison between the candidate and the benchmark
comparison AS (
  SELECT
    c.candidate_id,
    c.directorate,
    c.role,
    c.grade,
    c.tv_name,
    c.tgv_name,
    c.score AS user_score,
    f.score_type,
    f.baseline_score,
    CASE 
      WHEN f.score_type = 'numeric' THEN 
        CASE 
          WHEN f.tv_name IN ('PAPI_Z', 'PAPI_K') THEN 
            ROUND(((2 * f.baseline_score::numeric - c.score::numeric) / f.baseline_score::numeric) * 100, 2)
          ELSE 
            ROUND((c.score::numeric / f.baseline_score::numeric) * 100, 2)
        END
      ELSE
        CASE 
          WHEN f.tv_name = 'CliftonStrengths' THEN
            CASE WHEN c.score::numeric > 0 THEN 100 ELSE 0 END
          ELSE
            CASE WHEN c.score::numeric = 1 THEN 100 ELSE 0 END
        END
    END AS tv_match_rate
  FROM candidate_tables c
  LEFT JOIN final_baseline f USING (tv_id)
),
-- calucalte the TGV match rate
tgv_scored AS (
  SELECT
    candidate_id,
    directorate,
    role,
    grade,
    tgv_name,
    ROUND(AVG(tv_match_rate), 2) AS tgv_match_rate
  FROM comparison
  GROUP BY candidate_id, directorate, role, grade, tgv_name
),
--  calucalte the weighetd TGV match_rate
weighted_tgv AS (
  SELECT
    t.*,
    vc.tgv_weights,
    COALESCE(
      NULLIF((vc.tgv_weights ->> t.tgv_name), '')::numeric,
      0.125
    ) AS tgv_weight
  FROM tgv_scored t
  CROSS JOIN vacancy_config vc
),
-- calculate the final match_rate
final_match AS (
  SELECT
    candidate_id,
    directorate,
    role,
    grade,
    ROUND(SUM(tgv_match_rate * tgv_weight) / NULLIF(SUM(tgv_weight), 0), 2) AS final_match_rate
  FROM weighted_tgv
  GROUP BY candidate_id, directorate, role, grade
),
-- combine all the epxepcted output
final_output AS (
  SELECT
    c.candidate_id as employee_id,
    c.directorate,
    c.role,
    c.grade,
    c.tv_name,
    c.tgv_name,
    c.baseline_score,      
    c.user_score,
    c.tv_match_rate,
    t.tgv_match_rate,
    fm.final_match_rate
  FROM comparison c
  LEFT JOIN tgv_scored t USING (candidate_id, tgv_name)
  LEFT JOIN weighted_tgv w USING (candidate_id, tgv_name)
  LEFT JOIN final_match fm USING (candidate_id)
)

SELECT *
FROM final_output
ORDER BY employee_id, tgv_name, tv_name;
