from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import PromptTemplate
from langchain import LLMChain

LLM = ChatOpenAI(model_name="gpt-3.5-turbo", 
                 openai_api_key="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",
                 streaming=True, 
                 callbacks=[StreamingStdOutCallbackHandler()],
                 temperature=0.7,
                )

# LLM = ChatOpenAI(model_name="gpt-3.5-turbo", 
#                  openai_api_key="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",
#                  streaming=False, 
#                  callbacks=[StreamingStdOutCallbackHandler()],
#                  temperature=0.7,
#                 )

tutorial_generation_prompt = """
You are a tutorial generator for AWS EC2 deployment.
Based on the project structure and the AWS documentation given below, 
you have to give a complete, detailed, and coherent deployment tutorial for this project.
**Important"": You must output details about how to deploy this specific project. For each subpoint, if involved terminal operation, give some linux shell commands. If involved operation in aws console, give detailed guide on each step.

The project structure is {project_structure} 
Here are some useful AWS documentation {aws_documentation}.

The ultimate goal is to allow the user to be able to follow the tutorial to deploy the project in real industrial situations.
You don't have to include too much details about security group setting or similar stuffs.
Don't give up until you finished the entire tutorial.
You can use the following template to generate the tutorial:
{tutorial_template}
"""

tutorial_template = """
# Deploying [Your Application Name] to AWS EC2: A Comprehensive Guide

## 1. Introduction
- **Objective**: Understand the purpose and significance of deploying this application on EC2.
- **Brief Overview**: A concise overview of deploying this type of application on EC2.
- **Advantages of deploying on AWS EC2**: Elaborate on the benefits, cost efficiency, scalability, etc.

## 2. Prerequisites
- **System Requirements**: Specific OS, browser, or tools.
- **Dependencies**: Any software that must be pre-installed.
- **Knowledge Base**: Assumed prior knowledge (e.g., Node.js, Python, etc.)

## 3. Setting Up the EC2 Instance
- **Choosing the Right EC2 Instance**
  - Description: Different instance types and their advantages.
  - Command/Action: `aws ec2 describe-instance-types --query 'InstanceTypes[?ProcessorInfo.ThreadPerCore==`2`].{Name:InstanceType}' --output table` (Lists instances with 2 threads per core as an example.)
  
- **Launching an Instance**
  - **Step 1**: Navigate to the EC2 dashboard in the AWS Console.
  - **Step 2**: Click on 'Launch Instance'.
  - **Step 3**: Select an Amazon Machine Image (AMI), e.g., choose the latest Ubuntu Server.
  - **Step 4**: Choose the instance type (as identified earlier).
  - **Step 5**: Configure instance, storage, and tags.
  - **Step 6**: Configure the security group to allow inbound traffic on port 80 and 443 for HTTP and HTTPS, respectively.

- **Accessing the Instance**
  - Command/Action: `ssh -i /path/to/your/key.pem ubuntu@your-ec2-ip-address`
  
## 4. Setting Up the Web Server
- **Choosing a Web Server**: Discussion on Apache vs. Nginx vs. others. Here we'll assume Nginx.
  
- **Installing Nginx**
  - Command/Action: 
    ```bash
    sudo apt update
    sudo apt install nginx
    ```

- **Starting and Enabling Nginx**
  - Command/Action:
    ```bash
    sudo systemctl start nginx
    sudo systemctl enable nginx
    ```

- **Configuring Nginx for Your Application**
  - **Step 1**: Navigate to `/etc/nginx/sites-available/`.
  - **Step 2**: Create or modify a configuration file, e.g., `sudo nano your-app`.
  - **Step 3**: Modify the configuration to point to your application's entry point (e.g., for a Node.js app or a static website).
  - **Step 4**: Create a symlink to `/etc/nginx/sites-enabled/`.
  - Command/Action: `sudo ln -s /etc/nginx/sites-available/your-app /etc/nginx/sites-enabled/`
  
- **Testing Nginx Configuration and Restarting**
  - Command/Action:
    ```bash
    sudo nginx -t
    sudo systemctl restart nginx
    ```

## 5. Deploying the Web Application
- **Uploading Your Code**
  - **Using SCP**: Command/Action: `scp -i /path/to/your/key.pem /path/to/your/local/app ubuntu@your-ec2-ip-address:/path/on/your/server`
  
- **Installing Dependencies (Node.js example)**
  - Command/Action:
    ```bash
    cd /path/on/your/server
    npm install
    ```

- **Setting Up a Reverse Proxy (if using a backend server like Node.js)**
  - **Step 1**: Modify the Nginx configuration in `/etc/nginx/sites-available/your-app` to set up a reverse proxy.
  - **Step 2**: Test the Nginx configuration and reload: 
    ```bash
    sudo nginx -t
    sudo systemctl reload nginx
    ```

- **Setting Up a Database (PostgreSQL example)**
  - **Step 1**: Install PostgreSQL: `sudo apt install postgresql postgresql-contrib`
  - **Step 2**: Access the PostgreSQL shell and set up your database.
  - **Step 3**: Modify your application configuration to connect to the database.
  
- **Starting Your Application (Node.js example)**
  - Command/Action:
    ```bash
    node /path/on/your/server/app.js
    ```

- **Setting Up a Process Manager (PM2 for Node.js)**
  - Command/Action:
    ```bash
    npm install pm2 -g
    pm2 start /path/on/your/server/app.js
    ```

- **Testing the Deployment**
  - Access the application in your browser using the EC2 IP address or domain name.


## 6. Setting Up a Domain Name (Optional)
- **Domain Registration**: Where and how to buy a domain name.
- **Configuring DNS**: Pointing domain name to EC2 instance IP using Route 53 or other DNS services.
- **SSL Certificate**: Steps to generate and configure a free SSL using Let's Encrypt or other providers.

## 7. Monitoring and Scaling
- **CloudWatch**: Setting up metrics, alarms, and logs.
- **Auto-scaling**: Based on load, how to set up auto-scaling to handle traffic spikes.
- **Health Checks**: Ensuring your app is always healthy and running.

## 8. Backup and Recovery
- **Regular Backups**: Using AWS services like snapshots for EC2 and backup for RDS.
- **Disaster Recovery**: Steps to recover if something goes wrong, restoring from backup.
- **Best Practices**: Regular audits, keeping backups at different regions, etc.

## 9. Conclusion and Next Steps
- **Clean-Up**: Terminating resources to avoid costs.
- **Advanced Deployment Strategies**: Introduction to Docker, Kubernetes, CI/CD pipelines.
- **Feedback Loop**: Encouraging the community to contribute, report issues, or seek clarification.
- **Acknowledgements**: Any references, tools, or resources that aided in the tutorial's creation.

"""

tutorial_generation_template = PromptTemplate(
    input_variables=["project_structure", "aws_documentation", "tutorial_template"],
    template=tutorial_generation_prompt,
)


tutorial_generation_chain = LLMChain(llm=LLM, prompt=tutorial_generation_template)

demo_project_structure = """ - 📂 **your-project-name/**
  - 📂 **.vscode/** (Optional: for VS Code settings)
    - 📄 `settings.json`
  - 📂 **src/**
    - 📂 **config/**
      - 📄 `database.ts`
      - 📄 `config.ts`
    - 📂 **controllers/**
      - 📄 `user.controller.ts`
      - 📄 `post.controller.ts`
      ... (other controllers)
    - 📂 **models/**
      - 📄 `user.model.ts`
      - 📄 `post.model.ts`
      ... (other models)
    - 📂 **routes/**
      - 📄 `index.ts`
      - 📄 `user.routes.ts`
      - 📄 `post.routes.ts`
      ... (other routes)
    - 📂 **middlewares/**
      - 📄 `auth.middleware.ts`
      ... (other middlewares)
    - 📂 **services/**
      - 📄 `mail.service.ts`
      ... (other services)
    - 📂 **types/** (For TypeScript type definitions)
      - 📄 `user.type.ts`
      ... (other types)
    - 📂 **utils/**
      - 📄 `logger.ts`
      ... (other utilities)
    - 📄 `app.ts` (or `server.ts`)
    - 📄 `index.ts` (Entry point)
  - 📂 **dist/** (Compiled JavaScript files - this directory is auto-generated when you compile your TypeScript code)
  - 📂 **node_modules/** (Generated by npm or yarn; contains third-party libraries)
  - 📂 **tests/** (For your unit/integration tests)
    - 📄 `user.test.ts`
    ... (other tests)
  - 📄 `.gitignore`
  - 📄 `package.json`
  - 📄 `package-lock.json` or `yarn.lock`
  - 📄 `tsconfig.json`
  - 📄 `README.md`
"""


# result = tutorial_generation_chain({"project_structure": demo_project_structure, 
#                                     "aws_documentation": "AWS Documentation Unavailable", 
#                                     "tutorial_template": tutorial_template})
# for chunk in result:
#     print(chunk)