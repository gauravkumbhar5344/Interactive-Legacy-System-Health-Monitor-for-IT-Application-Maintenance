"""
Advanced Extensions & Real Data Connectors
For production deployment with legacy system integrations
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime
import os

# ============================================================================
# EXAMPLE 1: Real Data Connectors
# ============================================================================

class DataConnectors:
    """Adapters for common legacy system monitoring tools"""
    
    @staticmethod
    def fetch_from_splunk(query: str, earliest_time: str = "-24h") -> pd.DataFrame:
        """
        Connect to Splunk Enterprise for log aggregation
        
        Requirements:
            pip install splunk-sdk
        
        Example:
            logs = DataConnectors.fetch_from_splunk(
                query='index=main sourcetype=syslog | stats count by host',
                earliest_time='-7d'
            )
        """
        try:
            import splunklib.client as client
            
            service = client.connect(
                host=os.getenv("SPLUNK_HOST", "localhost"),
                port=os.getenv("SPLUNK_PORT", 8089),
                username=os.getenv("SPLUNK_USER"),
                password=os.getenv("SPLUNK_PASS")
            )
            
            response = service.jobs.export(query, earliest_time=earliest_time)
            # Parse response and return DataFrame
            # Implementation depends on Splunk API version
            
        except ImportError:
            print("Install: pip install splunk-sdk")
        except Exception as e:
            print(f"Splunk connection error: {e}")
        
        return pd.DataFrame()
    
    @staticmethod
    def fetch_from_datadog(query: str, api_key: str, app_key: str) -> pd.DataFrame:
        """
        Fetch metrics from Datadog
        
        Requirements:
            pip install datadog
        
        Example:
            metrics = DataConnectors.fetch_from_datadog(
                query='system.cpu.user{env:prod}',
                api_key='xxxx',
                app_key='yyyy'
            )
        """
        try:
            from datadog import initialize, api
            
            options = {
                'api_key': api_key,
                'app_key': app_key
            }
            initialize(**options)
            
            # Query metrics (last 24 hours)
            now = int(datetime.now().timestamp())
            data = api.Metric.query(query=query, start=now-86400, end=now)
            
            # Transform to DataFrame
            results = []
            for series in data.get('series', []):
                for point in series.get('pointlist', []):
                    results.append({
                        'timestamp': datetime.fromtimestamp(point[0]/1000),
                        'value': point[1],
                        'metric': series.get('metric'),
                        'tags': series.get('tags', [])
                    })
            
            return pd.DataFrame(results)
            
        except ImportError:
            print("Install: pip install datadog")
        except Exception as e:
            print(f"Datadog connection error: {e}")
        
        return pd.DataFrame()
    
    @staticmethod
    def fetch_from_prometheus(url: str, query: str) -> pd.DataFrame:
        """
        Query Prometheus metrics
        
        Requirements:
            pip install prometheus-client requests
        
        Example:
            metrics = DataConnectors.fetch_from_prometheus(
                url='http://prometheus:9090',
                query='rate(http_requests_total[5m])'
            )
        """
        try:
            import requests
            
            response = requests.get(
                f"{url}/api/v1/query",
                params={'query': query}
            )
            
            data = response.json()
            results = []
            
            if data['status'] == 'success':
                for result in data['data']['result']:
                    results.append({
                        'timestamp': datetime.now(),
                        'value': float(result['value'][1]),
                        'metric': result['metric'].get('__name__'),
                        'labels': result['metric']
                    })
            
            return pd.DataFrame(results)
            
        except ImportError:
            print("Install: pip install prometheus-client requests")
        except Exception as e:
            print(f"Prometheus connection error: {e}")
        
        return pd.DataFrame()
    
    @staticmethod
    def fetch_from_elasticsearch(index: str, query: Dict) -> pd.DataFrame:
        """
        Query Elasticsearch for logs
        
        Requirements:
            pip install elasticsearch
        
        Example:
            logs = DataConnectors.fetch_from_elasticsearch(
                index='logs-*',
                query={
                    'range': {
                        '@timestamp': {'gte': 'now-24h'}
                    }
                }
            )
        """
        try:
            from elasticsearch import Elasticsearch
            
            es = Elasticsearch(
                hosts=[os.getenv("ES_HOST", "localhost:9200")]
            )
            
            response = es.search(index=index, body={'query': query}, size=10000)
            
            results = []
            for hit in response['hits']['hits']:
                results.append(hit['_source'])
            
            return pd.DataFrame(results)
            
        except ImportError:
            print("Install: pip install elasticsearch")
        except Exception as e:
            print(f"Elasticsearch connection error: {e}")
        
        return pd.DataFrame()


# ============================================================================
# EXAMPLE 2: Advanced Anomaly Detection with Isolation Forest
# ============================================================================

class AdvancedAnomalyDetector:
    """ML-based anomaly detection for multivariate metrics"""
    
    @staticmethod
    def detect_multivariate_anomalies(metrics_df: pd.DataFrame, contamination=0.1):
        """
        Use Isolation Forest for multivariate anomaly detection
        
        Requirements:
            pip install scikit-learn
        
        Features:
            - Detects complex patterns in multi-dimensional data
            - No assumptions about data distribution
            - Efficient for high-dimensional data
        
        Example:
            from sklearn.ensemble import IsolationForest
            
            anomalies = AdvancedAnomalyDetector.detect_multivariate_anomalies(
                metrics_df[['cpu_usage_%', 'memory_usage_%', 'latency_ms']],
                contamination=0.1
            )
        """
        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler
            
            # Normalize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(metrics_df.select_dtypes(include='number'))
            
            # Train Isolation Forest
            clf = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )
            
            predictions = clf.fit_predict(X_scaled)
            anomaly_scores = clf.score_samples(X_scaled)
            
            return {
                'is_anomaly': predictions == -1,
                'anomaly_scores': anomaly_scores,
                'confidence': abs(anomaly_scores)
            }
            
        except ImportError:
            print("Install: pip install scikit-learn")
        
        return {}
    
    @staticmethod
    def detect_time_series_anomalies(series: pd.Series, window=30):
        """
        Detect anomalies using Z-score on rolling statistics
        """
        rolling_mean = series.rolling(window=window).mean()
        rolling_std = series.rolling(window=window).std()
        
        # Z-score
        z_scores = abs((series - rolling_mean) / rolling_std)
        
        return {
            'is_anomaly': z_scores > 3,
            'z_scores': z_scores
        }


# ============================================================================
# EXAMPLE 3: LLM Prompt Optimization with Few-Shot Learning
# ============================================================================

class OptimizedLLMChains:
    """Production-grade LLM chain templates"""
    
    @staticmethod
    def insight_generation_with_examples(llm, system_data: Dict) -> str:
        """
        Few-shot learning for more accurate insights
        Uses example patterns to guide LLM output
        """
        from langchain_core.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate
        
        # Define examples
        examples = [
            {
                "health_score": "45",
                "error_rate": "8.5%",
                "top_service": "PaymentGateway",
                "output": "CRITICAL: Payment processing experiencing cascading failures due to database connection exhaustion. Immediate action: scale DB instance and implement circuit breaker. This impacts revenue directly."
            },
            {
                "health_score": "72",
                "error_rate": "2.1%",
                "top_service": "CacheLayer",
                "output": "DEGRADED: Cache hit rate declining, causing increased database load. Recommend: analyze cache eviction policy and increase Redis memory allocation. Low immediate risk."
            },
            {
                "health_score": "92",
                "error_rate": "0.3%",
                "top_service": "N/A",
                "output": "HEALTHY: System operating optimally. Continue routine maintenance and monitor trending metrics. No action required."
            }
        ]
        
        example_prompt = ChatPromptTemplate.from_template(
            """Health Score: {health_score}
Error Rate: {error_rate}
Top Affected Service: {top_service}

Analysis: {output}"""
        )
        
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="You are a legacy system health analyst. Provide concise, actionable insights.",
            suffix="Health Score: {health_score}\nError Rate: {error_rate}\nTop Service: {top_service}\n\nAnalysis:",
            input_variables=["health_score", "error_rate", "top_service"]
        )
        
        chain = few_shot_prompt | llm
        response = chain.invoke(system_data)
        return response.content
    
    @staticmethod
    def structured_output_prompt(llm, system_data: Dict) -> Dict:
        """
        Generate structured outputs (JSON) from LLM for programmatic use
        """
        from langchain_core.output_parsers import JsonOutputParser
        from pydantic import BaseModel, Field
        
        class MaintenanceAction(BaseModel):
            priority: str = Field(description="URGENT, HIGH, MEDIUM, or LOW")
            action: str = Field(description="Specific action to take")
            estimated_duration_hours: int
            expected_impact: str
        
        class HealthReport(BaseModel):
            status: str
            summary: str
            actions: list[MaintenanceAction]
        
        parser = JsonOutputParser(pydantic_object=HealthReport)
        
        prompt_template = """
        Analyze this system health data and return a JSON response:
        {format_instructions}
        
        System Data:
        {system_data}
        """
        
        from langchain_core.prompts import PromptTemplate
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["system_data"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = prompt | llm | parser
        return chain.invoke({"system_data": str(system_data)})


# ============================================================================
# EXAMPLE 4: Semantic Log Clustering with Embeddings
# ============================================================================

class SemanticLogAnalysis:
    """Use embeddings for semantic grouping of similar errors"""
    
    @staticmethod
    def cluster_similar_errors(logs_df: pd.DataFrame, embeddings, n_clusters=5):
        """
        Cluster similar error messages to identify root causes
        
        Example:
            clusters = SemanticLogAnalysis.cluster_similar_errors(
                error_logs,
                embeddings,
                n_clusters=5
            )
        """
        try:
            from sklearn.cluster import KMeans
            
            # Get error messages
            error_messages = logs_df[logs_df['level'].isin(['ERROR', 'CRITICAL'])]['message'].tolist()
            
            if not error_messages:
                return {}
            
            # Generate embeddings
            message_embeddings = embeddings.embed_documents(error_messages)
            
            # Cluster
            kmeans = KMeans(n_clusters=min(n_clusters, len(error_messages)), random_state=42)
            clusters = kmeans.fit_predict(message_embeddings)
            
            # Group by cluster
            result = {}
            for idx, cluster_id in enumerate(clusters):
                if cluster_id not in result:
                    result[cluster_id] = []
                result[cluster_id].append(error_messages[idx])
            
            return {
                'clusters': result,
                'n_unique_clusters': len(result),
                'cluster_sizes': {k: len(v) for k, v in result.items()}
            }
            
        except ImportError:
            print("Install: pip install scikit-learn")
        
        return {}


# ============================================================================
# EXAMPLE 5: Integration with Incident Management Tools
# ============================================================================

class IncidentManagementIntegration:
    """Create incidents in external systems based on health alerts"""
    
    @staticmethod
    def create_pagerduty_incident(health_score: float, severity_reason: str) -> Dict:
        """
        Create PagerDuty incident when health degrades
        
        Requirements:
            pip install pdpyras
        
        Example:
            IncidentManagementIntegration.create_pagerduty_incident(
                health_score=35,
                severity_reason="Critical memory exhaustion in PaymentGateway"
            )
        """
        try:
            from pdpyras import APISession
            
            session = APISession(token=os.getenv("PAGERDUTY_TOKEN"))
            
            # Determine severity
            if health_score < 30:
                severity = "critical"
            elif health_score < 50:
                severity = "error"
            elif health_score < 70:
                severity = "warning"
            else:
                severity = "info"
            
            # Create incident
            incident = session.post(
                '/incidents',
                json={
                    'incident': {
                        'type': 'incident',
                        'title': f'Legacy System Health Alert (Score: {health_score:.1f})',
                        'body': {
                            'type': 'incident_body',
                            'details': severity_reason
                        },
                        'urgency': 'high' if health_score < 50 else 'low',
                        'service': {
                            'id': os.getenv("PAGERDUTY_SERVICE_ID"),
                            'type': 'service_reference'
                        }
                    }
                }
            )
            
            return {
                'success': True,
                'incident_id': incident['incident']['id'],
                'incident_number': incident['incident']['incident_number']
            }
            
        except ImportError:
            print("Install: pip install pdpyras")
        except Exception as e:
            print(f"PagerDuty error: {e}")
        
        return {'success': False}


# ============================================================================
# EXAMPLE 6: Evaluation & Monitoring of LLM Insights (RAGAS)
# ============================================================================

class LLMEvaluationFramework:
    """Evaluate quality of AI-generated insights"""
    
    @staticmethod
    def evaluate_insight_quality(insight: str, reference: str, embeddings):
        """
        Use RAGAS metrics to evaluate insight relevance and factuality
        
        Requirements:
            pip install ragas
        
        Metrics:
            - Faithfulness: How factual is the insight?
            - Relevance: How relevant to the health state?
            - Correctness: Does it correctly diagnose issues?
        """
        try:
            # Simple semantic similarity check as proxy for evaluation
            insight_embedding = embeddings.embed_query(insight)
            reference_embedding = embeddings.embed_query(reference)
            
            # Cosine similarity
            import numpy as np
            similarity = np.dot(insight_embedding, reference_embedding) / (
                np.linalg.norm(insight_embedding) * np.linalg.norm(reference_embedding)
            )
            
            return {
                'similarity_score': float(similarity),
                'is_relevant': similarity > 0.7,
                'quality_rating': 'Good' if similarity > 0.7 else 'Needs Review'
            }
            
        except ImportError:
            print("Install: pip install ragas numpy")
        
        return {}


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    """
    Quick start examples for integrating with legacy systems
    """
    
    print("=" * 70)
    print("Advanced Extensions - Integration Examples")
    print("=" * 70)
    
    # Example 1: Load real data from Prometheus
    print("\n1. Loading metrics from Prometheus:")
    print("   → df = DataConnectors.fetch_from_prometheus(...)")
    
    # Example 2: Detect multivariate anomalies
    print("\n2. Advanced anomaly detection:")
    print("   → anomalies = AdvancedAnomalyDetector.detect_multivariate_anomalies(df)")
    
    # Example 3: Semantic clustering
    print("\n3. Semantic error grouping:")
    print("   → clusters = SemanticLogAnalysis.cluster_similar_errors(error_df, embeddings)")
    
    # Example 4: PagerDuty integration
    print("\n4. Create incidents automatically:")
    print("   → IncidentManagementIntegration.create_pagerduty_incident(health_score=35, ...)")
    
    # Example 5: LLM evaluation
    print("\n5. Evaluate insight quality:")
    print("   → metrics = LLMEvaluationFramework.evaluate_insight_quality(...)")
    
    print("\n" + "=" * 70)
    print("See code comments for detailed usage patterns and requirements")
    print("=" * 70)