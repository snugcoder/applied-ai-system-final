classDiagram
    class Owner {
        -name: str
        -email: str
        -_time_available: float
        +get_time_available(): float
        +add_pet(pet: Pet): void
    }

    class Pet {
        -name: str
        -species: str
        -breed: str
        -age: int
        -tasks: List~Task~
        +add_task(task: Task): void
        +get_tasks(): List~Task~
    }

    class Task {
        -name: str
        -duration: float
        -priority: int
        -category: str
        -description: str
        -completed: bool
        +mark_complete(): void
    }

    class Scheduler {
        -owner: Owner
        +generate_plan(date): List~Task~
        +get_all_tasks(): List~Task~
        +get_plan_explanation(): str
    }

    class ScheduleVerifier {
        +verify(plan: List~Task~, owner: Owner): VerificationResult
    }

    class VerificationResult {
        -approved: bool
        -feedback: str
        -suggestions: List~str~
    }

    Owner "1" *-- "*" Pet : owns
    Pet "1" *-- "*" Task : has
    Scheduler "1" --> "1" Owner : schedules for
    Scheduler "1" --> "*" Task : arranges
    ScheduleVerifier "1" --> "1" Scheduler : verifies output of
    ScheduleVerifier "1" --> "1" VerificationResult : returns