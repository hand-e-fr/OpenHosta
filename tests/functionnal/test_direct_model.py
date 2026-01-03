from OpenHosta import config

answer = "**"
print(answer,  end="")
for i in range(10):
    response = config.DefaultModel.api_call(
        llm_args={"max_tokens": 20},
        messages=[
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": answer}
            ])
    
    new_token = config.DefaultModel.get_response_content(response)
    answer += new_token
    print(new_token, end="", flush=True)
    
    
    
    