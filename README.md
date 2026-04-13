# PawPal+ - AI Final

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the script by typing ```python main.py``` in the terminal.

# Applied AI System Final Planning

## Planning 

This project must do something useful with AI -> Plan & Complete a task step by step
-> Reliability or Testing System : because the system I am improving is a To Do list + Scheduler, I want it to be able to know when the schedule will not work. Thats crucial. It should be able to move things around and ask the Owner if thats alright. 

## Data Flow

(Owner → Pet → Task) and scheduling flow (Scheduler → Verification → Result)
A more detailed example is provided in ```dataflow_uml.md```

## Testing

Reliability Signal: A complete product that passes testing is a scheduler that regenerates a schedule based on the LLM evaluator optimizer pattern. When the LLM evaluates the schedule against metrics like greedy scheduling and omptimizing schedules for time constraints and priority, and provide a useful feedback, that would indicate a complete project. 