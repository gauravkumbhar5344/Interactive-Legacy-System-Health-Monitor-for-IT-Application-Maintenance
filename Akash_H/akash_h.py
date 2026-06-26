"""
Legacy System Health Monitor - AI-Driven Dashboard
POC Implementation with Groq LLM and HuggingFace Embeddings
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import plotly.graph_objects as go
import plotly.express as px
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
import warnings
warnings.filterwarnings("ignore")

# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

st.set_page_config(
    page_title="Legacy System Health Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_llm():
    """Initialize Groq LLM"""
    return ChatGroq(
        groq_api_key="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",
        model_name="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=500
    )

@st.cache_resource
def load_embeddings():
    """Initialize HuggingFace embeddings"""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

# ============================================================================
# SYNTHETIC DATA GENERATOR
# ============================================================================

class SyntheticLegacyDataGenerator:
    """Generate realistic legacy system data for POC"""
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        
    def generate_system_logs(self, n_entries=1000, anomaly_rate=0.15):
        """Generate synthetic system logs with anomalies"""
        now = datetime.now()
        timestamps = [now - timedelta(minutes=i) for i in range(n_entries)]
        timestamps.reverse()
        
        log_levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
        services = ["AuthService", "DBCluster", "MessageQueue", "CacheLayer", "APIGateway", "PaymentGw"]
        
        logs = []
        for i, ts in enumerate(timestamps):
            # Inject anomalies
            if np.random.random() < anomaly_rate:
                level = np.random.choice(["ERROR", "CRITICAL"])
                response_time = np.random.randint(5000, 15000)
                message = np.random.choice([
                    "Connection timeout exceeded",
                    "Memory usage critical (95%)",
                    "Database query exceeded threshold",
                    "Service unavailable",
                    "High latency detected",
                    "Resource exhaustion warning"
                ])
            else:
                level = np.random.choice(log_levels[:3])
                response_time = np.random.randint(100, 1000)
                message = np.random.choice([
                    "Request processed successfully",
                    "Transaction completed",
                    "Health check passed",
                    "Cache hit recorded",
                    "Load balanced"
                ])
            
            logs.append({
                "timestamp": ts,
                "service": np.random.choice(services),
                "level": level,
                "response_time_ms": response_time,
                "message": message,
                "user_count": np.random.randint(100, 10000)
            })
        
        return pd.DataFrame(logs)
    
    def generate_performance_metrics(self, n_points=144):
        """Generate hourly performance metrics (6 days)"""
        now = datetime.now()
        hours = [now - timedelta(hours=i) for i in range(n_points)]
        hours.reverse()
        
        metrics = []
        base_cpu = 45
        base_memory = 60
        base_latency = 250
        
        for i, ts in enumerate(hours):
            # Inject anomalies in specific windows
            if 100 < i < 110 or 130 < i < 140:
                cpu = base_cpu + np.random.randint(30, 50)
                memory = base_memory + np.random.randint(25, 35)
                latency = base_latency + np.random.randint(200, 400)
                disk_io = 85
            else:
                cpu = base_cpu + np.random.randint(-5, 15)
                memory = base_memory + np.random.randint(-5, 10)
                latency = base_latency + np.random.randint(-50, 100)
                disk_io = np.random.randint(30, 70)
            
            metrics.append({
                "timestamp": ts,
                "cpu_usage_%": min(100, cpu),
                "memory_usage_%": min(100, memory),
                "latency_ms": latency,
                "disk_io_%": disk_io,
                "requests_per_sec": np.random.randint(50, 500),
                "error_rate_%": max(0, (cpu - 40) / 2) if cpu > 40 else np.random.uniform(0, 2)
            })
        
        return pd.DataFrame(metrics)
    
    def generate_incidents(self, n_incidents=15):
        """Generate historical incident records"""
        now = datetime.now()
        incidents = []
        
        for i in range(n_incidents):
            days_ago = np.random.randint(1, 30)
            incident_ts = now - timedelta(days=days_ago)
            resolution_ts = incident_ts + timedelta(hours=np.random.randint(1, 24))
            
            incidents.append({
                "incident_id": f"INC-{2024001 + i}",
                "timestamp": incident_ts,
                "resolved_at": resolution_ts,
                "severity": np.random.choice(["Low", "Medium", "High", "Critical"]),
                "service_affected": np.random.choice(["AuthService", "DBCluster", "MessageQueue", "CacheLayer", "APIGateway"]),
                "root_cause": np.random.choice([
                    "Memory leak in connection pool",
                    "Database deadlock",
                    "Cascade failure from upstream service",
                    "Resource exhaustion",
                    "Network timeout",
                    "Configuration mismatch"
                ]),
                "resolution_time_hours": np.random.randint(1, 24),
                "impact_users": np.random.randint(100, 100000)
            })
        
        return pd.DataFrame(incidents)

# ============================================================================
# ANOMALY DETECTION & HEALTH SCORING
# ============================================================================

class HealthAnalyzer:
    """Analyze system health and detect anomalies"""
    
    @staticmethod
    def detect_log_anomalies(logs_df: pd.DataFrame) -> Dict:
        """Detect anomalies in logs using statistical methods"""
        errors = logs_df[logs_df['level'].isin(['ERROR', 'CRITICAL'])]
        error_rate = len(errors) / len(logs_df) if len(logs_df) > 0 else 0
        
        # High latency detection
        high_latency = logs_df[logs_df['response_time_ms'] > 3000]
        high_latency_rate = len(high_latency) / len(logs_df) if len(logs_df) > 0 else 0
        
        # Service-level anomalies
        service_errors = errors.groupby('service').size()
        
        return {
            "error_rate": error_rate,
            "high_latency_rate": high_latency_rate,
            "critical_logs_count": len(logs_df[logs_df['level'] == 'CRITICAL']),
            "service_errors": service_errors.to_dict() if len(service_errors) > 0 else {},
            "avg_response_time_ms": logs_df['response_time_ms'].mean()
        }
    
    @staticmethod
    def detect_metric_anomalies(metrics_df: pd.DataFrame) -> Dict:
        """Detect anomalies in performance metrics"""
        anomalies = {
            "high_cpu_events": len(metrics_df[metrics_df['cpu_usage_%'] > 80]),
            "high_memory_events": len(metrics_df[metrics_df['memory_usage_%'] > 85]),
            "high_latency_events": len(metrics_df[metrics_df['latency_ms'] > 600]),
            "high_error_rate_events": len(metrics_df[metrics_df['error_rate_%'] > 5])
        }
        return anomalies
    
    @staticmethod
    def calculate_health_score(logs_anomalies: Dict, metric_anomalies: Dict, incidents_df: pd.DataFrame) -> Tuple[float, str]:
        """Calculate overall system health score (0-100)"""
        score = 100.0
        
        # Log-based penalties
        score -= logs_anomalies.get('error_rate', 0) * 100 * 0.3
        score -= logs_anomalies.get('high_latency_rate', 0) * 100 * 0.2
        score -= min(logs_anomalies.get('critical_logs_count', 0) * 5, 20)
        
        # Metric-based penalties
        score -= min(metric_anomalies.get('high_cpu_events', 0) * 0.5, 15)
        score -= min(metric_anomalies.get('high_memory_events', 0) * 0.5, 15)
        score -= min(metric_anomalies.get('high_latency_events', 0) * 0.3, 10)
        
        # Recent incident penalty
        if len(incidents_df) > 0:
            recent_incidents = incidents_df[incidents_df['timestamp'] > datetime.now() - timedelta(days=7)]
            score -= len(recent_incidents) * 3
        
        score = max(0, min(100, score))
        
        # Status determination
        if score >= 80:
            status = "🟢 Healthy"
        elif score >= 60:
            status = "🟡 Degraded"
        elif score >= 40:
            status = "🔴 Critical"
        else:
            status = "⛔ Offline"
        
        return score, status

# ============================================================================
# GROQ-POWERED INSIGHTS GENERATION
# ============================================================================

def generate_ai_insights(system_summary: Dict, llm) -> str:
    """Generate natural language insights using Groq"""
    prompt = ChatPromptTemplate.from_template("""
    Analyze this legacy system monitoring data and provide a concise (3-4 sentences) 
    executive summary with actionable maintenance recommendations.
    
    Data:
    - Health Score: {health_score}
    - Critical Logs: {critical_logs}
    - High Latency Events: {high_latency_events}
    - Error Rate: {error_rate}%
    - Top Issue: {top_issue}
    
    Focus on: what's wrong, why it matters, what to fix first.
    """)
    
    chain = prompt | llm
    response = chain.invoke(system_summary)
    return response.content

def generate_maintenance_report(logs_df, metrics_df, incidents_df, health_score, llm):
    """Generate prioritized maintenance action items"""
    prompt = ChatPromptTemplate.from_template("""
    Create a prioritized maintenance checklist (max 5 items) for a legacy system with:
    - Health Score: {health_score}
    - Recent Error Count: {error_count}
    - Avg Latency: {avg_latency}ms
    - Recent Incidents: {incident_count}
    
    Format as: [PRIORITY] Action - Expected Impact
    Where PRIORITY is: URGENT, HIGH, MEDIUM, LOW
    """)
    
    chain = prompt | llm
    response = chain.invoke({
        "health_score": health_score,
        "error_count": len(logs_df[logs_df['level'].isin(['ERROR', 'CRITICAL'])]),
        "avg_latency": metrics_df['latency_ms'].mean(),
        "incident_count": len(incidents_df[incidents_df['timestamp'] > datetime.now() - timedelta(days=7)])
    })
    return response.content

# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    st.title("🏥 Legacy System Health Monitor")
    st.markdown("*AI-Driven Intelligence for Legacy Application Maintenance*")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        #api_key = st.text_input("Groq API Key", type="password", value=st.secrets.get("GROQ_API_KEY", ""))
        api_key = "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"

        if api_key:
            # st.secrets["GROQ_API_KEY"] = api_key
            st.success("✓ API Key configured")
        
        st.divider()
        refresh_interval = st.slider("Data Refresh Interval (min)", 1, 60, 5)
        anomaly_threshold = st.slider("Anomaly Sensitivity", 0.05, 0.3, 0.15)
        
        st.divider()
        st.subheader("Data Generation")
        if st.button("🔄 Regenerate Synthetic Data"):
            st.session_state.data_refreshed = True
            st.rerun()
    
    # Initialize/Load Data
    if 'data_refreshed' not in st.session_state or st.session_state.data_refreshed:
        generator = SyntheticLegacyDataGenerator(seed=np.random.randint(0, 10000))
        st.session_state.logs_df = generator.generate_system_logs(anomaly_rate=anomaly_threshold)
        st.session_state.metrics_df = generator.generate_performance_metrics()
        st.session_state.incidents_df = generator.generate_incidents()
        st.session_state.data_refreshed = False
    
    logs_df = st.session_state.logs_df
    metrics_df = st.session_state.metrics_df
    incidents_df = st.session_state.incidents_df
    
    # Health Analysis
    analyzer = HealthAnalyzer()
    log_anomalies = analyzer.detect_log_anomalies(logs_df)
    metric_anomalies = analyzer.detect_metric_anomalies(metrics_df)
    health_score, status = analyzer.calculate_health_score(log_anomalies, metric_anomalies, incidents_df)
    
    # ========================================================================
    # KPI DASHBOARD
    # ========================================================================
    st.subheader("📊 System Health Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Health Score",
            f"{health_score:.1f}/100",
            f"{health_score - 75:.1f}",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "System Status",
            status,
            "Updated now"
        )
    
    with col3:
        error_count = len(logs_df[logs_df['level'].isin(['ERROR', 'CRITICAL'])])
        st.metric(
            "Critical Events",
            error_count,
            f"{(log_anomalies['error_rate'] * 100):.1f}% error rate"
        )
    
    with col4:
        recent_incidents = len(incidents_df[incidents_df['timestamp'] > datetime.now() - timedelta(days=7)])
        st.metric(
            "7-Day Incidents",
            recent_incidents,
            f"Avg {incidents_df['resolution_time_hours'].mean():.1f}h resolution"
        )
    
    st.divider()
    
    # ========================================================================
    # PERFORMANCE CHARTS
    # ========================================================================
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 Performance Metrics")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=metrics_df['timestamp'],
            y=metrics_df['cpu_usage_%'],
            name='CPU Usage',
            line=dict(color='#FF6B6B')
        ))
        fig1.add_trace(go.Scatter(
            x=metrics_df['timestamp'],
            y=metrics_df['memory_usage_%'],
            name='Memory Usage',
            line=dict(color='#4ECDC4')
        ))
        fig1.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Warning Threshold")
        fig1.update_layout(
            title="CPU & Memory Utilization",
            xaxis_title="Time",
            yaxis_title="Usage %",
            hovermode='x unified',
            height=350
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        st.subheader("⚡ Response Latency & Error Rate")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=metrics_df['timestamp'],
            y=metrics_df['latency_ms'],
            name='Latency (ms)',
            yaxis='y1',
            line=dict(color='#95E1D3')
        ))
        fig2.add_trace(go.Scatter(
            x=metrics_df['timestamp'],
            y=metrics_df['error_rate_%'],
            name='Error Rate %',
            yaxis='y2',
            line=dict(color='#F38181')
        ))
        fig2.update_layout(
            title="System Performance",
            xaxis_title="Time",
            yaxis=dict(title="Latency (ms)"),
            yaxis2=dict(title="Error Rate %", overlaying='y', side='right'),
            hovermode='x unified',
            height=350
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    
    # ========================================================================
    # ANOMALY DETECTION RESULTS
    # ========================================================================
    st.subheader("🚨 Detected Anomalies")
    
    col_anom1, col_anom2, col_anom3 = st.columns(3)
    
    with col_anom1:
        with st.expander("📋 Log Anomalies", expanded=True):
            st.metric("Error Rate", f"{log_anomalies['error_rate']*100:.2f}%")
            st.metric("High Latency Incidents", f"{log_anomalies['high_latency_rate']*100:.2f}%")
            st.metric("Critical Logs", log_anomalies['critical_logs_count'])
            st.metric("Avg Response Time", f"{log_anomalies['avg_response_time_ms']:.0f}ms")
    
    with col_anom2:
        with st.expander("📊 Metric Anomalies", expanded=True):
            st.metric("High CPU Events", metric_anomalies['high_cpu_events'])
            st.metric("High Memory Events", metric_anomalies['high_memory_events'])
            st.metric("High Latency Events", metric_anomalies['high_latency_events'])
            st.metric("High Error Rate Events", metric_anomalies['high_error_rate_events'])
    
    with col_anom3:
        with st.expander("🔧 Service Health", expanded=True):
            service_errors = log_anomalies.get('service_errors', {})
            if service_errors:
                services_data = pd.DataFrame(list(service_errors.items()), columns=['Service', 'Errors'])
                st.bar_chart(services_data.set_index('Service'))
            else:
                st.info("No service-level errors detected")
    
    st.divider()
    
    # ========================================================================
    # AI-POWERED INSIGHTS
    # ========================================================================
    if api_key:
        st.subheader("🤖 AI-Powered Insights (Groq)")
        
        if st.button("Generate AI Insights", key="ai_insights"):
            with st.spinner("Generating insights from Groq..."):
                try:
                    llm = load_llm()
                    
                    system_summary = {
                        "health_score": f"{health_score:.1f}",
                        "critical_logs": log_anomalies['critical_logs_count'],
                        "high_latency_events": metric_anomalies['high_latency_events'],
                        "error_rate": f"{log_anomalies['error_rate']*100:.2f}",
                        "top_issue": max(log_anomalies.get('service_errors', {}).items(), 
                                       key=lambda x: x[1], default=('N/A', 0))[0]
                    }
                    
                    insights = generate_ai_insights(system_summary, llm)
                    
                    st.info(f"**Executive Summary**\n\n{insights}")
                
                except Exception as e:
                    st.error(f"⚠️ Error generating insights: {str(e)}")
                    st.info("Ensure GROQ_API_KEY is valid. Get it from https://console.groq.com")
        
        if st.button("Generate Maintenance Report", key="maintenance_report"):
            with st.spinner("Generating maintenance report from Groq..."):
                try:
                    llm = load_llm()
                    report = generate_maintenance_report(logs_df, metrics_df, incidents_df, 
                                                        f"{health_score:.1f}", llm)
                    st.success("**Prioritized Action Items**")
                    st.markdown(report)
                
                except Exception as e:
                    st.error(f"⚠️ Error generating report: {str(e)}")
    else:
        st.warning("⚠️ Add Groq API Key in sidebar to enable AI insights")
    
    st.divider()
    
    # ========================================================================
    # INCIDENT HISTORY & DATA EXPORT
    # ========================================================================
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        st.subheader("📋 Recent Incidents")
        recent_incidents = incidents_df.sort_values('timestamp', ascending=False).head(10)
        display_cols = ['incident_id', 'timestamp', 'severity', 'service_affected', 'resolution_time_hours']
        st.dataframe(recent_incidents[display_cols], use_container_width=True)
    
    with col_export2:
        st.subheader("📥 Export Data")
        
        # CSV Export
        csv_logs = logs_df.to_csv(index=False)
        st.download_button(
            label="Download Logs (CSV)",
            data=csv_logs,
            file_name=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        csv_metrics = metrics_df.to_csv(index=False)
        st.download_button(
            label="Download Metrics (CSV)",
            data=csv_metrics,
            file_name=f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # JSON Report
        report_json = json.dumps({
            "health_score": health_score,
            "status": status,
            "generated_at": datetime.now().isoformat(),
            "log_anomalies": log_anomalies,
            "metric_anomalies": metric_anomalies,
            "recent_incidents": len(incidents_df[incidents_df['timestamp'] > datetime.now() - timedelta(days=7)])
        }, indent=2, default=str)
        
        st.download_button(
            label="Download Report (JSON)",
            data=report_json,
            file_name=f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    st.divider()
    
    # Footer
    st.caption(
        "Hello guys CJ here| POC v1.0 | "
        
    )

if __name__ == "__main__":
    main()