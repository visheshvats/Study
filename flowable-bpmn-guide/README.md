# Flowable BPMN Guide & Example

This guide explains **Flowable** and **BPMN 2.0** (Business Process Model and Notation) with a practical Java example.

## What is Flowable?

Flowable is a light-weight, open-source business process engine written in Java. It can deploy BPMN 2.0 process definitions (defined in XML) and execute them. It handles:
- **State Management**: Keeping track of where a process is (e.g., "Waiting for Manager Approval").
- **Persistence**: Saving the state to a database (default H2, supports MySQL, Postgres, etc.).
- **Task Management**: Assigning tasks to users or groups.
- **Service Orchestration**: Calling Java code, REST APIs, or scripts as part of the process.

## What is BPMN 2.0?
**BPMN** stands for **Business Process Model and Notation**. It is a standard graphical notation for drawing business processes in a workflow.
- **Events** (Circles): Start, End, Timer.
- **Tasks** (Rounded Rectangles): User Task, Service Task (system calls), Script Task.
- **Gateways** (Diamonds): Decisions (Exclusive Gateway), Parallel execution (Parallel Gateway).
- **Sequence Flows** (Arrows): Determine the path of execution.

## The Example Process: Holiday Request

We will build a simple "Holiday Request" process:
1.  **Start Event**: The process begins.
2.  **User Task**: The employee requests a holiday (simulated by input).
3.  **User Task**: The manager approves or rejects the request.
4.  **Exclusive Gateway (Decision)**:
    - If **Approved**: Go to the "Enter Holidays in External System" (Service Task).
    - If **Rejected**: Send a rejection email (simulated Service Task).
5.  **End Event**: The process finishes.

## Project Structure
```text
flowable-bpmn-guide/
├── pom.xml                 # Maven dependencies
├── README.md               # This file
├── src
│   ├── main
│   │   ├── java
│   │   │   └── org
│   │   │       └── flowable
│   │   │           ├── HolidayRequest.java      # Main class to run the engine
│   │   │           └── CallExternalSystemDelegate.java # Java Logic for Service Task
│   │   └── resources
│   │       └── holiday-request.bpmn20.xml       # The Process Definition
```

## How to Run

1.  Make sure you have Java (JDK 8+) and Maven installed.
2.  Open a terminal in this folder.
3.  Run the application:
    ```bash
    mvn clean compile exec:java -Dexec.mainClass="org.flowable.HolidayRequest"
    ```

You should see output in the console asking for input, simulating the manager logic, and finally printing the process outcome.
