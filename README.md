**AirBrain AI**
Built on Alephium blockchain, AirBrain AI is building Composable generative AI Agents Protocol (CAAP) which allows users to build personalized AI agents within minutes on-chain for use cases such as crypto alpha research, NFT research, learn about crypto and DeFi, generate ideas, create marketing content  etc.

**About AirBrain AI**
We are transforming how individuals perform crypto tasks with the Composable Generative AI Agents Protocol (CAAP). This revolutionary platform enables users to construct custom AI agents in a matter of minutes. From crypto and NFT research to generating unique marketing content, CAAP realizes the potential of generative AI in simplifying numerous use-cases within the evolving crypto AI landscape.  

**Web**
https://www.airbrain.co/  

**Video and demo**
https://player.hourone.ai/c018610d64c64928877bf8337f456aec  

**Pitch deck**
https://drive.google.com/file/d/1YbRBvd7SBfZAEtNe2e34esuVDdBRBVUP/view?usp=drive_link  


**AirBrain AI Python backend setup guide.**  

Install git  
      Based on your OS, install git  

Setup app  
1. Install Python 3.10.11  
2. Install VCRuntime from this link https://learn.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022  
3. Install Python 3.8 and create python virtual enviornment (details https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/  )   
      pip install virtualenv  
      python -m venv airbrain-backend  
4. Activate virtual environment  
      source bacairbrain-backend/Scripts/activate    
5. Install packages  
    pip install -r requirements.txt  
6. Create a file ".env" and enter following key value pairs  
      FLASK_APP=app
      OPENAI_API_KEY=<Your OPENAI API key>
7. Run the app with command "flask run"




