
# Introduction
This repo is a barebones implementation of how to turn your streamlit application into a micro-SaaS.

Some key things implemented :
- Authenticate users using Google OAuth 2.0
- Manage user subscriptions with Stripe integration
- Restrict access to the application based on subscription status

## Streamlit app: Smart Quiz

Smart Quiz is an intelligent learning companion that generates practice questions and answers based on study material provided in PDF format.

## Features

- Upload study material in PDF format
- Automatically generate practice questions based on the uploaded content
- Select specific questions to generate answers


## Technologies Used

- Python
- Streamlit
- Langchain
- OpenAI 
- Chroma
- PyPDF2
- Google OAuth 2.0
- Stripe API

# Installation

1. Clone the repository:

   ```bash
    git clone https://github.com/sid-thephysicskid/microsaas-example.git
    cd microsaas-example
    ```
2. Install the required dependencies using Poetry:
    ```bash
    poetry install
    ```
    Poetry creates virtual environments in the ```~/Library/Caches/poetry``` directory by default. You can also choose to create a virtual environment in the current folder by setting the virtualenvs.in-project option to true.

    ```bash
    poetry config virtualenvs.in-project true 
    ```


    Here's an excellent video if you are new to Poetry: https://www.youtube.com/watch?v=0f3moPe_bhk

3. Configuration:

    Google OAuth 2.0:
    - Set up a new project in the Google Cloud Console (https://console.cloud.google.com/)
    - Configure the OAuth consent screen and add the necessary scopes
    - Create OAuth 2.0 credentials and obtain the client ID and client secret
    - Set the authorized redirect URIs in the Google Cloud Console

    Stripe:
    - Create a Stripe account and obtain the API key (use test mode for testing)
    - Set up a product and pricing plan in the Stripe dashboard
    - Configure the necessary webhooks for subscription management
    - Set the redirect link to your app for post-subscription confirmation

    OpenAI API key:
    - Obtain your API key here: https://platform.openai.com/api-keys

    Now rename `secrets.toml.example` -> `secrets.toml` under `.streamlit` folder and set up the necessary variables as needed, namely:
    ```bash
    OPENAI_API_KEY = "sk-"
    testing_mode = true
    payment_provider = "stripe" #bmac if using Buy Me A Coffee
    stripe_api_key_test = "sk_test_..." #only needed if using Stripe
    stripe_api_key = "sk_live_..." #only needed if using Stripe
    stripe_link = "https://buy.stripe.com/..." #only needed if using Stripe
    stripe_link_test = "https://buy.stripe.com/test_..." #only needed if using Stripe
    client_id = "590..."
    client_secret = "GO..."
    redirect_url_test = 'http://localhost:8501/'
    redirect_url = "https://your_deployed_app_url..."
    bmac_api_key = "ey..." #only needed if using buy me a coffee
    bmac_link = "https://www.buymeacoffee.com/..." #only needed if using buy me a coffee
    ```


4. Run the application:
    ```bash
    poetry run streamlit run main.py
    ```

## Usage
- Once launched, click on the "Login with Google" button to authenticate using your Google account

- If you are not a subscribed user, click on the "Subscribe now!" button to subscribe to the service. Checkout via stripe and since it configured to run in 'test' mode by default (aka no actual payments will be processed), feel free to use this fake CC number for testing - `4242 4242 4242 4242` with expiration date of `12/34` and 3 digit CVC code `567`

- If you've configured stripe to redirect the user to your app's URL after payment (set to `http://localhost:8501/` by default if hosted locally), they will be redirected back here and will be prompted to login again and use the app.

- Upload a PDF file containing your study material
- The application will generate practice questions based on the uploaded content
- Select the desired questions and click on "Generate Answer" to get detailed answers
- To cancel your subscription, click on the "Cancel Subscription" button
- If you are not subscribed or your subscription is canceled, you will be logged out and redirected to the login page

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.