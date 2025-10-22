# import streamlit as st
# from supabase import create_client, Client
# import pandas as pd
# import plotly.express as px
# import openai

# # =========================
# # CONFIG
# # =========================
# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# openai.api_key = OPENROUTER_API_KEY
# openai.api_base = "https://openrouter.ai/api/v1"

# st.set_page_config(page_title="Talent Intelligence Dashboard", layout="wide")

# # =========================
# # SIDEBAR INPUTS
# # =========================
# st.sidebar.header("🔍 New Job Vacancy Configuration")

# role_name = st.sidebar.text_input("Role Name", "Data Analyst")
# job_level = st.sidebar.selectbox(
#     "Job Level", ["Junior", "Middle", "Senior"], index=1)
# role_purpose = st.sidebar.text_area(
#     "Role Purpose",
#     "Responsible for analyzing data, creating reports, and supporting business decisions."
# )

# selected_ids = st.sidebar.text_input(
#     "Benchmark Employee IDs (comma separated)",
#     "312,335,175"
# )
# run_query = st.sidebar.button("🚀 Generate Insights")

# # =========================
# # MAIN PAGE
# # =========================
# st.title("🎯 Talent Intelligence Dashboard")
# st.markdown(
#     "This dashboard dynamically analyzes talent fit and generates AI-powered job profiles based on benchmark employees."
# )

# # =========================
# # LOGIC
# # =========================
# if run_query:
#     with st.spinner("Running SQL query and generating insights..."):
#         # 1️⃣ Insert a new job vacancy config
#         benchmark_ids = [int(i.strip())
#                          for i in selected_ids.split(",") if i.strip().isdigit()]
#         job_data = {
#             "role_name": role_name,
#             "job_level": job_level,
#             "role_purpose": role_purpose,
#             "selected_talent_ids": benchmark_ids,
#         }

#         # Insert into Supabase table
#         insert_response = supabase.table(
#             "talent_benchmarks").insert(job_data).execute()
#         job_vacancy_id = insert_response.data[0]["job_vacancy_id"]

#         # 2️⃣ Call the Postgres function directly
#         response = supabase.rpc(
#             "run_talent_benchmark", {"p_job_vacancy_id": job_vacancy_id}
#         ).execute()

#         df = pd.DataFrame(response.data)

#         if df.empty:
#             st.warning("No data found for this configuration.")
#         else:
#             st.success("✅ Query executed successfully!")
#             st.dataframe(df.head())

#             # 3️⃣ Generate AI-powered Job Profile using OpenRouter (LLM)
#             prompt = f"""
#             You are an HR talent intelligence analyst. 
#             Generate a structured job profile for the following:
#             Role: {role_name}
#             Level: {job_level}
#             Purpose: {role_purpose}
#             Based on performance data from benchmark employees: {benchmark_ids}.
#             Return three sections:
#             1. Job Requirements (skills, experience, tools)
#             2. Job Description (summary of the role)
#             3. Key Competencies (behaviors or traits linked to success)
#             Format neatly in Markdown.
#             """

#             ai_response = openai.ChatCompletion.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "system", "content": "You are an HR analytics assistant."},
#                           {"role": "user", "content": prompt}],
#                 temperature=0.7,
#             )
#             profile_text = ai_response.choices[0].message.content

#             # 4️⃣ Display AI-Generated Job Profile
#             st.subheader("🤖 AI-Generated Job Profile")
#             st.markdown(profile_text)

#             # 5️⃣ Visualizations
#             st.subheader("📊 Match Rate Overview")
#             fig = px.bar(
#                 df.sort_values("final_match_rate", ascending=False),
#                 x="employee_id",
#                 y="final_match_rate",
#                 color="grade",
#                 title="Final Match Rate per Employee",
#                 text_auto=True
#             )
#             st.plotly_chart(fig, use_container_width=True)

#             st.subheader("🌈 Top Strengths and Gaps (TGV)")
#             tgv_mean = df.groupby("tgv_name")[
#                 "tv_match_rate"].mean().reset_index()
#             fig2 = px.bar(
#                 tgv_mean,
#                 x="tgv_name",
#                 y="tv_match_rate",
#                 title="Average Match Rate by TGV",
#                 text_auto=True
#             )
#             st.plotly_chart(fig2, use_container_width=True)

#             # Summary
#             best_candidate = df.groupby("employee_id")[
#                 "final_match_rate"].mean().idxmax()
#             best_score = df.loc[df["employee_id"] ==
#                                 best_candidate, "final_match_rate"].mean()
#             st.success(
#                 f"🏆 Top Candidate: **Employee {best_candidate}** with match rate **{best_score:.2f}%**")

# else:
#     st.info("👈 Configure job parameters and click **Generate Insights** to start.")

import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import openai

# =========================
# CONFIG
# =========================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

st.set_page_config(page_title="Talent Intelligence Dashboard", layout="wide")

# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("🔍 New Job Vacancy Configuration")

role_name = st.sidebar.text_input("Role Name", "Data Analyst")
job_level = st.sidebar.selectbox(
    "Job Level", ["Junior", "Middle", "Senior"], index=1)
role_purpose = st.sidebar.text_area(
    "Role Purpose",
    "Responsible for analyzing data, creating reports, and supporting business decisions."
)

selected_ids = st.sidebar.text_input(
    "Benchmark Employee IDs (comma separated)",
    "312,335,175"
)
run_query = st.sidebar.button("🚀 Generate Insights")

# =========================
# MAIN PAGE
# =========================
st.title("🎯 Talent Intelligence Dashboard")
st.markdown(
    "This dashboard dynamically analyzes talent fit and generates AI-powered job profiles based on benchmark employees."
)

# =========================
# LOGIC
# =========================
if run_query:
    with st.spinner("Running SQL query and generating insights..."):
        # 1️⃣ Insert a new job vacancy config
        benchmark_ids = [int(i.strip())
                         for i in selected_ids.split(",") if i.strip().isdigit()]
        job_data = {
            "role_name": role_name,
            "job_level": job_level,
            "role_purpose": role_purpose,
            "selected_talent_ids": benchmark_ids,
        }

        # Insert into Supabase table
        insert_response = supabase.table(
            "talent_benchmarks").insert(job_data).execute()
        job_vacancy_id = insert_response.data[0]["job_vacancy_id"]

        # 2️⃣ Run SQL function dynamically using the new job_vacancy_id
        response = supabase.rpc("run_talent_benchmark", {
            "p_job_vacancy_id": job_vacancy_id
        }).execute()
        df = pd.DataFrame(response.data)

        if df.empty:
            st.warning("No data found for this configuration.")
        else:
            st.success("✅ Query executed successfully!")
            st.dataframe(df.head())

            # 3️⃣ Generate AI-powered Job Profile using OpenRouter (LLM)
            prompt = f"""
            You are an HR talent intelligence analyst. 
            Generate a structured job profile for the following:
            Role: {role_name}
            Level: {job_level}
            Purpose: {role_purpose}
            Based on performance data from benchmark employees: {benchmark_ids}.
            Return three sections:
            1. Job Requirements (skills, experience, tools)
            2. Job Description (summary of the role)
            3. Key Competencies (behaviors or traits linked to success)
            Format neatly in Markdown.
            """

            ai_response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are an HR analytics assistant."},
                          {"role": "user", "content": prompt}],
                temperature=0.7,
            )
            profile_text = ai_response.choices[0].message.content

            # 4️⃣ Display AI-Generated Job Profile
            st.subheader("🤖 AI-Generated Job Profile")
            st.markdown(profile_text)

            # 5️⃣ Visualizations
            st.subheader("📊 Match Rate Overview")
            fig = px.bar(
                df.sort_values("final_match_rate", ascending=False),
                x="employee_id",
                y="final_match_rate",
                color="grade",
                title="Final Match Rate per Employee",
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🌈 Top Strengths and Gaps (TGV)")
            tgv_mean = df.groupby("tgv_name")[
                "tv_match_rate"].mean().reset_index()
            fig2 = px.bar(
                tgv_mean,
                x="tgv_name",
                y="tv_match_rate",
                title="Average Match Rate by TGV",
                text_auto=True
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Summary
            best_candidate = df.groupby("employee_id")[
                "final_match_rate"].mean().idxmax()
            best_score = df.loc[df["employee_id"] ==
                                best_candidate, "final_match_rate"].mean()
            st.success(
                f"🏆 Top Candidate: **Employee {best_candidate}** with match rate **{best_score:.2f}%**")

            # =========================
            # Radar Chart: Candidate vs Benchmark
            # =========================
            st.subheader("📈 Candidate vs Benchmark TGV Profile")

            # Compute benchmark median per TGV
            benchmark_median = df.groupby(
                "tgv_name")["tgv_match_rate"].median().reset_index()
            benchmark_median.rename(
                columns={"tgv_match_rate": "benchmark"}, inplace=True)

            # Compute each candidate's mean TGV match rate
            candidate_tgv = df.groupby(["employee_id", "tgv_name"])[
                "tgv_match_rate"].mean().reset_index()

            # Merge benchmark
            radar_df = candidate_tgv.merge(benchmark_median, on="tgv_name")

            # Select candidate to visualize
            candidate_list = df["employee_id"].unique().tolist()
            selected_candidate = st.selectbox(
                "Select Candidate for Radar Chart", candidate_list)

            candidate_data = radar_df[radar_df["employee_id"]
                                      == selected_candidate]

            # Plot radar chart using Plotly
            fig_radar = px.line_polar(
                r=[*candidate_data["tgv_match_rate"],
                    candidate_data["tgv_match_rate"].iloc[0]],
                theta=[*candidate_data["tgv_name"],
                       candidate_data["tgv_name"].iloc[0]],
                line_close=True,
                markers=True,
                name=f"Candidate {selected_candidate}",
            )

            # Add benchmark trace
            fig_radar.add_scatterpolar(
                r=[*candidate_data["benchmark"],
                    candidate_data["benchmark"].iloc[0]],
                theta=[*candidate_data["tgv_name"],
                       candidate_data["tgv_name"].iloc[0]],
                line_close=True,
                marker=dict(color="red"),
                name="Benchmark Median",
            )

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title=f"Candidate {selected_candidate} vs Benchmark TGV Profile"
            )

            st.plotly_chart(fig_radar, use_container_width=True)

else:
    st.info("👈 Configure job parameters and click **Generate Insights** to start.")
