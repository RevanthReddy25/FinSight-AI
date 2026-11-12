from decimal import Decimal


class FinancialProject:
    """
    Represents the financial information of a business project.
    """

    def __init__(
        self,
        project_id: int,
        project_name: str,
        client_name: str,
        budget: Decimal,
        revenue: Decimal,
        expenditure: Decimal,
    ) -> None:

        # Validate project information
        if project_id <= 0:
            raise ValueError("Project ID must be positive.")

        if not project_name.strip():
            raise ValueError("Project name cannot be empty.")

        if not client_name.strip():
            raise ValueError("Client name cannot be empty.")

        if budget < 0 or revenue < 0 or expenditure < 0:
            raise ValueError("Financial amounts cannot be negative.")

        # Store project information
        self.project_id = project_id
        self.project_name = project_name
        self.client_name = client_name
        self.budget = budget
        self.revenue = revenue
        self.expenditure = expenditure