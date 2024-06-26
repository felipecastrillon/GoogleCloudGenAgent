import gradio as gr
from agent import Agent
import config
import random
import time

def main():
  llm_agent = Agent()
  
  if config.APP_TYPE == "search":

    app = gr.Interface(fn=llm_agent.search, inputs=gr.Textbox(label="Query"),
                        outputs=[gr.Textbox(label="Response"), gr.Textbox(label="Snippets")])

  elif config.APP_TYPE == "chat":

    with gr.Blocks() as app:
      chatbot = gr.Chatbot()
      msg = gr.Textbox()
      clear = gr.ClearButton([msg, chatbot])

      def respond(message, chat_history):
          bot_message = llm_agent.chat(message)
          chat_history.append((message, bot_message))
          time.sleep(2)
          return "", chat_history

      msg.submit(respond, [msg, chatbot], [msg, chatbot])
    
  else:
    raise ValueError("splitter input must be one of the following values [\"text\",\"chat\"]") 

  app.launch(server_name="0.0.0.0", server_port=8080)


if __name__ == '__main__':
  main()

