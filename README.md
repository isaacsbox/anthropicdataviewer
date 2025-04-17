
# Query Anthropic's Conversation Data from Claude.AI

This is a Streamlit application to query the 1 million collected and categorised conversations users had with Claude.ai (one of the biggest public LLM chatbots). It currently allows string matching queries (e.g., "compliance") and multiple strings (e.g., "compliance, legal").

Plotly is used for interactive bar charts, along with optional table views. 

## Quickstart
1. `pip install requirements.txt`
2. `streamlit run main.py`

(all datasets are included)

## Dataset

This data was made available as part of the "Anthropic Economic Index" which seeks to monitor AI usage over time (it's also part of Anthropic's Memorandum deal with the UK Government to support AI development)

Anthropic first categorised all the conversations into the 20,000+ O*NET task descriptors (using Claude AI and a hierarchical method). These task descriptors are the 'task_name' values in the dataset. 

#### Interaction Type

All conversations under a certain task were categorised according to the **type of interaction**:

- Directive: Human delegates complete task execution to AI with minimal interaction
- Feedback Loop: Human and AI engage in iterative dialogue to complete task with human mainly providing feedback from the environment
- Task Iteration: Human and AI engage in iterative dialogue to complete a task with the human refining the AI outputs
- Learning: Human seeks understanding and explanation rather than direct task completion
- Validation: Human uses AI to check or validate their own work
- Filtered: the conversations were filtered (i.e., blocked)


This allows you to see the nature of how people interact with the AI depending on the task. 

#### Volume

Percentage of all conversations that were that task. This gives a simple measure of how popular that task is.

#### Initial Reflections
We might be able to create aggregate scores to represent unusual data points - e.g., tasks that are popular but highly filtered, or tasks that are especially strong in one interaction type or another. 

Tasks high in being 'directive' are usually where the user has certainty or high knowledge of the task, whereas tasks high in 'learning' suggests users have significant uncertainty or low knowledge in that task (note that some task categories are more about learning and others more about checking, so this follows the change in interaction type)

