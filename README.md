create a venv with python 3.11 : python3.11 -m venv venv  
activate venv : source venv/bin/activate                                                           
install requirements : pip install -r requirements.txt                                          
start frontend : cd frontend -> open index.html                                        
start backend : cd backend -> uvicorn main:app --reload                                         
add a .env file and paste the openAI API key in this format (OPENAI_API_KEY = "***")



It is a simple RAG application in which we can upload pdf and ask questions related to that pdf


