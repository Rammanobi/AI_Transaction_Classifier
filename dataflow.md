# Data Flow
flowchart TD

    A[User Upload CSV]

    B[POST /jobs/upload]

    C[Validate File]

    D[Create Job Record]

    E[Status = Pending]

    F[Store File]

    G[Push Job to Redis]

    H[Return Job ID]

    I[Celery Worker Picks Job]

    J[Update Status = Processing]

    K[Read CSV]

    L[Row Validation]

    M[Valid Rows]

    N[Invalid Rows]

    O[Transaction Pipeline]

    P[RowError Table]

    Q[Data Cleaning]

    R[Duplicate Detection]

    S[Anomaly Detection]

    T[Save Transactions]

    U[Find Missing Categories]

    V[Batch LLM Classification]

    W[Update Categories]

    X[Generate Aggregates]

    Y[LLM Narrative Summary]

    Z[Store Job Summary]

    AA[Update Job Status = Completed]

    AB[GET Status]

    AC[GET Results]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H

    G --> I
    I --> J
    J --> K
    K --> L

    L --> M
    L --> N

    N --> P

    M --> O
    O --> Q
    Q --> R
    R --> S
    S --> T

    T --> U
    U --> V
    V --> W

    W --> X
    X --> Y
    Y --> Z
    Z --> AA

    AA --> AB
    AA --> AC