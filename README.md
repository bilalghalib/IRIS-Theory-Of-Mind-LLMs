LLMs develop a Theory of Mind representing the people they're talking to. What if this was expressed explicitly and if we could also request it tell us what it thinks we should know?

This is a first trial experimenting with these questions. I believe allowing someone to know what the LLM thinks of it, and to offer ways for people to refine their goals, beliefs, knowledge and other elements within the LLM will help people learn and grow while being assissted to get stuff done. 
https://arxiv.org/abs/2405.18870
<img width="1108" alt="Screenshot 2024-07-02 at 13 57 42" src="https://github.com/bilalghalib/IRIS-Theory-Of-Mind-LLMs/assets/3254792/69acd0fb-0510-4b10-a442-4cec89ccd223">

Experiment exposing the TOM to the users.
<img width="818" alt="demoScreenshot" src="https://github.com/bilalghalib/IRIS-Theory-Of-Mind-LLMs/assets/3254792/e514aeff-4548-40cb-a30f-def07c5f79be">

To run download code and open in terminal, and run python main. Be sure to update the API key and to have the includes needed.

## New graphical visualization

The `/get_tom_graph` endpoint returns an interactive Plotly chart that is shown in the chat UI when you click **Toggle Graph**.  Install the optional `plotly` package to enable this feature:

```bash
pip install plotly
```

Run the application with `python main.py` and open your browser to `http://localhost:5002`.

