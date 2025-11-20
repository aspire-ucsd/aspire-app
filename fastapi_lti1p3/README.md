# FastAPI LTI1p3

### [Quick Start](#quick-start-content)
- [Initialization](#initialization-content)
- [Register Routes](#register-routes-content)
- [Expose Headers](#expose-headers-content)
- [Tool Registration URL]()
- [Target Link URI](#target-link-uri-content)
- [Local Development](#local-development-content)

### Operation
- [Overview]()
- [Session Management]()
- [Tool Registration]()
- [Public JWK]()
- [Dependency Injection]()
- [Access Tokens]()
- [Platform API Keys]()

### Configuration
- [Config Variables]()
    - [AUTH_FRAME_REPO]()
    - [AUTH_FRAME_TEMPLATE]()
    - [AUTH_FRAME_TOKEN_TEMPLATE]()
    - [OIDC_AUTH_REDIRECT_URI]()
    - [OIDC_INITIATION_URL]()
    - [LAUNCH_BASE_PATH]()
    - [OIDC_AUTH_REQ_URL]()
    - [OIDC_TARGET_LINK_URI]()
    - [OAUTH_TOKEN_GET]()
    - [OAUTH_TOKEN_POST]()
    - [PLATFORM_JWK_URL]()
    - [TOOL_DOMAIN_NAME]()
    - [PLATFORM_ISS]()
    - [WEB_APP_TITLE]()
    - [WEB_APP_DESCRIPTION]()
    - [PLATFORM_JWK_URL]()
    - [LTI_PUBLIC_KEY]()
    - [LTI_PRIVATE_KEY]()
    - [DEVELOPER_KEY_SCOPES]()
    - [TOKEN_SCOPES]()

- [Template Overrides]()

### Routes
- [/lti/launch/init]()
- [/lti/launch/response]()
- [/lti/launch/response/token]()
- [/lti/public_jwk]()
- [/lti/register]()



## Quick Start {#quick-start-content}
This package is configured by default to function as a Canvas adapter, usage with other LTI compatible LMS's may require adjustment to the built-in launch routes and auth frame html templates.

#### Initialization {#initialization-content}
To get started launching your FastAPI application as an LTI, the package must be initialized at application startup with configuration settings matching the desired developer key content. bellow is an example config for the Canvas LMS using the default package launch routes and no access token scopes:

<p style="margin:0">
    <span 
        style="
            background-color: #333; 
            color:white; 
            padding:5px; 
            margin:0;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            "
    >
        main.py
    </span>
</p>

```py
from .init_app import init_app
from fastapi_lti1p3 import init_adapter_config, ConfigSettings

# Step 1: Create Config Object
lti_config = ConfigSettings(
    OIDC_AUTH_REQ_URL="https://sso.canvaslms.com/api/lti/authorize_redirect",
    OIDC_TARGET_LINK_URI="/launch", # This is the final target for the LTI launch process
    OAUTH_TOKEN_GET="https://example.instructure.com/login/oauth2/auth",
    OAUTH_TOKEN_POST="https://example.instructure.com/login/oauth2/token",
    PLATFORM_JWK_URL="https://sso.canvaslms.com/api/lti/security/jwks",
    TOOL_DOMAIN_NAME="https://your-tools-domain",
    PLATFORM_ISS="https://canvas.test.instructure.com",
    PLATFORM_JWK_URL="https://sso.canvaslms.com/api/lti/security/jwks"
    DEVELOPER_KEY_SCOPES=[
        "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
        "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly",
        "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
        "https://purl.imsglobal.org/spec/lti-ags/scope/score",
        "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly"
        ]
)

# Step 2: Initialize Config on startup
init_adapter_config(adapter_config)

#step 3: Start FastAPI
app = init_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


```

#### Register Routes {#register-routes-content}
The library comes packaged with all necessary routes to complete the OIDC launch process and establish a client-session. If using the libraries default base path and oidc urls in the config settings, all that is required is to import the routes and mount them to the app. 

``` py 
from fastapi_lti1p3 import routes
from main import app

app.include_router(routes.router)
```


#### Target Link URI {#target-link-uri-content}
The final step is to create the endpoint that will serve your content to the LMS, the route path to this endpoint must match the path set to the variable 'OIDC_TARGET_LINK_URI' in the configSettings. 

#### Local Development {#local-development-content}
As a result of necessitating session management post-OIDC auth flow for endpoint protection, a full implementation of this adapter to your FastAPI application will result in any protected endpoints being inaccessible without performing this auth flow and subsequently creating a valid session. It is possible to simulate the OIDC auth flow and launch steps for local development, this adapter has come packaged with a functional example of this simulated flow and allows for complete flexibility in modifying or bypassing this system.