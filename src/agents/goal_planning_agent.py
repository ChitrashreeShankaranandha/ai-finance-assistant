
from src.core.openai_client import get_openai_client

client = get_openai_client()

def calculate_goal_metrics(goal_amount: float, current_savings: float,
                            monthly_contribution: float, annual_return: float,
                            years: int) -> dict:
    """Calculate financial goal projections using compound interest math."""
    months       = years * 12
    monthly_rate = annual_return / 100 / 12

    # Future value of current savings
    fv_savings = current_savings * ((1 + monthly_rate) ** months)

    # Future value of monthly contributions (annuity formula)
    if monthly_rate > 0:
        fv_contributions = monthly_contribution * (
            ((1 + monthly_rate) ** months - 1) / monthly_rate
        )
    else:
        fv_contributions = monthly_contribution * months

    total_projected  = round(fv_savings + fv_contributions, 2)
    gap              = round(goal_amount - total_projected, 2)
    on_track         = total_projected >= goal_amount

    # Required monthly contribution to hit goal exactly
    if monthly_rate > 0:
        required_monthly = round(
            (goal_amount - fv_savings) * monthly_rate /
            (((1 + monthly_rate) ** months) - 1), 2
        )
    else:
        required_monthly = round((goal_amount - fv_savings) / months, 2)

    return {
        "goal_amount":          goal_amount,
        "current_savings":      current_savings,
        "monthly_contribution": monthly_contribution,
        "annual_return":        annual_return,
        "years":                years,
        "projected_value":      total_projected,
        "gap":                  gap,
        "on_track":             on_track,
        "required_monthly":     max(required_monthly, 0),
    }


def goal_planning_agent(
    goal_name:            str,
    goal_amount:          float,
    current_savings:      float,
    monthly_contribution: float,
    annual_return_pct:    float,
    years:                int,
    risk_profile:         str = "moderate"
) -> str:
    """
    Generates a personalized financial goal plan with GPT guidance.
    risk_profile options: conservative | moderate | aggressive
    """
    metrics = calculate_goal_metrics(
        goal_amount, current_savings,
        monthly_contribution, annual_return_pct, years
    )

    risk_profiles = {
        "conservative": "bonds and stable assets (expected 4-5% annual return)",
        "moderate":     "balanced mix of stocks and bonds (expected 6-8% annual return)",
        "aggressive":   "growth stocks and equity funds (expected 9-12% annual return)",
    }
    risk_description = risk_profiles.get(risk_profile, risk_profiles["moderate"])

    prompt = f"""
You are a financial education assistant helping a beginner plan for a financial goal.

GOAL DETAILS:
Goal Name:            {goal_name}
Target Amount:        ${metrics['goal_amount']:,.2f}
Current Savings:      ${metrics['current_savings']:,.2f}
Monthly Contribution: ${metrics['monthly_contribution']:,.2f}
Expected Annual Return: {metrics['annual_return']}%
Time Horizon:         {metrics['years']} years
Risk Profile:         {risk_profile} — {risk_description}

CALCULATED PROJECTIONS:
Projected Value:      ${metrics['projected_value']:,.2f}
On Track:             {"YES! Great job!" if metrics['on_track'] else "NOT YET — but fixable!"}
Gap:                  ${abs(metrics['gap']):,.2f} {"surplus" if metrics['on_track'] else "shortfall"}
Required Monthly:     ${metrics['required_monthly']:,.2f} to hit goal exactly

Please provide:
1. Clear summary of whether this person is on track for their {goal_name} goal
2. 3 specific actionable steps to improve their plan
3. How their {risk_profile} risk profile affects their investment strategy
4. One motivational insight about starting now vs waiting 1 year
5. Recommended asset allocation percentages for their risk profile

Always end with: "This is for educational purposes only and not financial advice."
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content
