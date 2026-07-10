import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.incident_engine import get_all_incidents

def show_page():
    st.markdown("<h2 style='margin-bottom: 5px;'>📊 Incident Analytics</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px;'>Enterprise metrics dashboard. Analysis of severity trends, risk profiles, departments, and SLA resolution indicators.</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Fetch data
    df = get_all_incidents()
    
    if df.empty:
        st.info("No data available to plot analytics. Log some incidents first.")
        return
        
    # Ensure correct types and fill blanks
    df['risk_score'] = pd.to_numeric(df['risk_score'], errors='coerce').fillna(0).astype(int)
    df['people_affected'] = pd.to_numeric(df['people_affected'], errors='coerce').fillna(0).astype(int)
    df['resolution_time_mins'] = pd.to_numeric(df['resolution_time_mins'], errors='coerce').fillna(0.0)
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['month_year'] = pd.to_datetime(df['timestamp']).dt.to_period('M').astype(str)
    
    # Global Plotly Theme Settings
    chart_layout = dict(
        paper_bgcolor='rgba(15, 23, 42, 0.4)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='#cbd5e1', family='Plus Jakarta Sans'),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor='#1e293b', zeroline=False),
        yaxis=dict(gridcolor='#1e293b', zeroline=False),
    )
    
    # ------------------ ROW 1 ------------------
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart 1: Category Distribution (Donut)
        st.markdown("<h5 style='color: #60a5fa;'>📂 Category/Type Distribution</h5>", unsafe_allow_html=True)
        cat_counts = df['incident_type'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        
        fig1 = px.pie(
            cat_counts, 
            names='Category', 
            values='Count',
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig1.update_layout(chart_layout)
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        # Chart 2: Severity Trend (Bar)
        st.markdown("<h5 style='color: #60a5fa;'>🌡 Severity Level Distribution</h5>", unsafe_allow_html=True)
        sev_counts = df['severity'].value_counts().reset_index()
        sev_counts.columns = ['Severity', 'Count']
        
        # Sort custom order
        severity_order = {'Critical': 0, 'Major': 1, 'Moderate': 2, 'Minor': 3}
        sev_counts['order'] = sev_counts['Severity'].map(severity_order).fillna(4)
        sev_counts = sev_counts.sort_values('order')
        
        color_map = {
            'Critical': '#ef4444',
            'Major': '#f59e0b',
            'Moderate': '#3b82f6',
            'Minor': '#10b981'
        }
        
        fig2 = px.bar(
            sev_counts,
            x='Severity',
            y='Count',
            color='Severity',
            color_discrete_map=color_map,
            category_orders={'Severity': ['Critical', 'Major', 'Moderate', 'Minor']}
        )
        fig2.update_layout(chart_layout)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        
    st.write("---")
    
    # ------------------ ROW 2 ------------------
    col3, col4 = st.columns(2)
    
    with col3:
        # Chart 3: Daily/Monthly Trend (Timeline line plot)
        st.markdown("<h5 style='color: #60a5fa;'>📈 Incident Reporting Trend (Daily)</h5>", unsafe_allow_html=True)
        trend_df = df.groupby('date').size().reset_index(name='Incidents')
        trend_df = trend_df.sort_values('date')
        
        fig3 = px.line(
            trend_df,
            x='date',
            y='Incidents',
            markers=True,
            line_shape='spline'
        )
        fig3.update_traces(line_color='#3b82f6', line_width=3, marker=dict(size=8, color='#60a5fa'))
        fig3.update_layout(chart_layout)
        st.plotly_chart(fig3, use_container_width=True)
        
    with col4:
        # Chart 4: Department Distribution (Horizontal Bar)
        st.markdown("<h5 style='color: #60a5fa;'>🏢 Department Involvement Breakdown</h5>", unsafe_allow_html=True)
        dept_counts = df['assigned_department'].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Count']
        dept_counts = dept_counts.sort_values('Count', ascending=True)
        
        fig4 = px.bar(
            dept_counts,
            y='Department',
            x='Count',
            orientation='h',
            color_discrete_sequence=['#a78bfa']
        )
        fig4.update_layout(chart_layout)
        st.plotly_chart(fig4, use_container_width=True)
        
    st.write("---")
    
    # ------------------ ROW 3 ------------------
    col5, col6 = st.columns(2)
    
    with col5:
        # Chart 5: Incident Heatmap (Incident Type vs Severity Grid)
        st.markdown("<h5 style='color: #60a5fa;'>🗺 Heatmap: Incident Type vs Severity</h5>", unsafe_allow_html=True)
        heatmap_data = pd.crosstab(df['incident_type'], df['severity'])
        
        # Ensure all standard severities are present in columns
        for col_name in ['Critical', 'Major', 'Moderate', 'Minor']:
            if col_name not in heatmap_data.columns:
                heatmap_data[col_name] = 0
                
        # Reorder columns
        heatmap_data = heatmap_data[['Critical', 'Major', 'Moderate', 'Minor']]
        
        fig5 = px.imshow(
            heatmap_data,
            text_auto=True,
            color_continuous_scale='Viridis',
            labels=dict(x="Severity", y="Category", color="Incidents")
        )
        fig5.update_layout(chart_layout)
        st.plotly_chart(fig5, use_container_width=True)
        
    with col6:
        # Chart 6: Priority Breakdown (Bar)
        st.markdown("<h5 style='color: #60a5fa;'>⚡ Response Priority Code Breakdown</h5>", unsafe_allow_html=True)
        priority_counts = df['priority'].value_counts().reset_index()
        priority_counts.columns = ['Priority', 'Count']
        
        # Sort priority
        priority_order = {'P1': 0, 'P2': 1, 'P3': 2, 'P4': 3}
        priority_counts['order'] = priority_counts['Priority'].map(priority_order).fillna(4)
        priority_counts = priority_counts.sort_values('order')
        
        fig6 = px.bar(
            priority_counts,
            x='Priority',
            y='Count',
            color='Priority',
            color_discrete_sequence=['#ef4444', '#f59e0b', '#3b82f6', '#10b981'],
            category_orders={'Priority': ['P1', 'P2', 'P3', 'P4']}
        )
        fig6.update_layout(chart_layout)
        fig6.update_layout(showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)
        
    st.write("---")
    
    # ------------------ ROW 4 ------------------
    col7, col8 = st.columns(2)
    
    with col7:
        # Chart 7: Risk Score Distribution (Box plot/Violin)
        st.markdown("<h5 style='color: #60a5fa;'>🎯 Incident Risk Score Distribution</h5>", unsafe_allow_html=True)
        fig7 = px.box(
            df,
            y='risk_score',
            points="all",
            color_discrete_sequence=['#fb7185'],
            labels={'risk_score': 'Risk Score (0-100)'}
        )
        fig7.update_layout(chart_layout)
        st.plotly_chart(fig7, use_container_width=True)
        
    with col8:
        # Chart 8: Resolution Time by Department (Bar)
        st.markdown("<h5 style='color: #60a5fa;'>⏳ Average Resolution Time by Team (Hours)</h5>", unsafe_allow_html=True)
        resolved_df = df[df["status"] == "Resolved"]
        
        if resolved_df.empty:
            st.markdown(
                """
                <div style="background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 40px; text-align: center; height: 350px; display: flex; align-items: center; justify-content: center;">
                    <span style="color: #94a3b8; font-style: italic;">No resolved incidents available to plot resolution time metrics.</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            resolved_df['resolution_hours'] = resolved_df['resolution_time_mins'] / 60.0
            res_df = resolved_df.groupby('assigned_department')['resolution_hours'].mean().reset_index(name='Avg Hours')
            res_df = res_df.sort_values('Avg Hours', ascending=False)
            
            fig8 = px.bar(
                res_df,
                x='assigned_department',
                y='Avg Hours',
                color='Avg Hours',
                color_continuous_scale='Plasma',
                labels={'assigned_department': 'Department', 'Avg Hours': 'Average Hours'}
            )
            fig8.update_layout(chart_layout)
            st.plotly_chart(fig8, use_container_width=True)
