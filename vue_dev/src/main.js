import { createApp, ref } from "vue"
import App from "./App.vue"
import VNetworkGraph from "v-network-graph"
import VueApexCharts from "vue3-apexcharts";
import "v-network-graph/lib/style.css"
import axios from "axios"

import HomePage from "./pages/HomePage.vue"
import DomainEditor from "./pages/DomainEditor.vue"
import StudentQuiz from "./pages/StudentQuiz.vue"
// import QuizAuthoring from "./pages/QuizAuthoring.vue"
import AdaptiveTutor from "./pages/AdaptiveTutor.vue"
// import SettingsPage from "./pages/SettingsPage.vue"
import StudentModel from "./pages/StudentModel.vue"
import ChangeRequests from "./pages/ChangeRequests.vue"

import "./styles/fonts.css"
import "./styles/body.css"


if (!window.contextData) {
   const urlParams = new URLSearchParams(window.location.search);
   const token = urlParams.get('token');
   window.contextData = JSON.parse(token)
}

const app = createApp(App)
app.use(VNetworkGraph)
app.use(VueApexCharts)

// ADD STUDENT VIEW COMPONENTS BELLOW
if (window.contextData.roles.split(",").includes("StudentEnrollment")) {
   app.component(StudentModel.name, StudentModel)
   .component(StudentQuiz.name, StudentQuiz)
   // .component(SettingsPage.name, SettingsPage)
   .component(AdaptiveTutor.name, AdaptiveTutor)
} 
// ADD SME VIEW COMPONENTS BELLOW
else {
   app.component(HomePage.name, HomePage)
      .component(DomainEditor.name, DomainEditor)
      // .component(QuizAuthoring.name, QuizAuthoring)
      .component(ChangeRequests.name, ChangeRequests)
      // .component(SettingsPage.name, SettingsPage)

}

app.provide("currentTab", ref("HomePage"));



function getSessionConfig() {
   return new Promise((resolve, reject) => {
      const contextData = window.contextData

      if (contextData.storage_target === "cookie") {
         resolve({key: "withCredentials", value: true})

      } else {
         let platformOrigin = new URL(contextData.oidc_auth_domain).origin
         let parent = window.parent || window.opener
         const storageTarget = contextData.storage_target

         let targetFrame = contextData.storage_target === "_parent" ? parent : parent.frames[storageTarget];
         const messageId = crypto.randomUUID()

         targetFrame.postMessage({
            "subject": "lti.get_data",
            "message_id": messageId,
            "key": contextData.session_storage_key,
         }, platformOrigin)

         window.addEventListener('message', async function handleResponse(event) {
            if (event.data.subject === "lti.get_data.response") {

               const splitContent = event.data.value.split('|')
               
               let result = {};
       
               for (let i = 0; i < splitContent.length; i += 2) {
                   result[splitContent[i]] = splitContent[i + 1];
               }

               resolve(
                  {
                     key: "headers", 
                     value: {[contextData.session_storage_key]: result[contextData.session_storage_key]}
                  })

            }

            if (event.data.error) {
               reject(new Error(`${event.data.error.code} - ${event.data.error.message}`))
            }
         })

         setTimeout(() => {
            reject(new Error("Error: Session ID retrieval timed out"))
         }, 5000)
      }
   })
}

axios.interceptors.request.use(async (config) => {
   // Causes infinite loop when making an API call (refresh session) from the interceptor function if this check is absent
   if (config?.value?.skipInterceptor || false) {

      delete config.value.skipInterceptor;
      // Remove the disable flag in header before sending the request
      config.headers = config.value
      return config;
  }
   try {
      const sessionConfig = await getSessionConfig()
      config[sessionConfig.key] = sessionConfig.value
      return config

   } catch (error) {
      return Promise.reject(error)
   }
})

function refreshSessionConfig() {
   return new Promise(
      (resolve, reject) => {
         const contextData = window.contextData

         if (contextData.storage_target === "cookie") {
            resolve()
         } else {
            // Why are you like this Canvas? Who hurt you?
            let platformOrigin = new URL(contextData.oidc_auth_domain).origin
            let parent = window.parent || window.opener
            const storageTarget = contextData.storage_target
            let targetFrame = contextData.storage_target === "_parent" ? parent : parent.frames[storageTarget];
            const messageId = crypto.randomUUID()

            targetFrame.postMessage({
               "subject": "lti.get_data",
               "message_id": messageId,
               "key": contextData.session_storage_key,
            }, platformOrigin)

            window.addEventListener('message', async function handleResponse(event) {
               if (event.data.subject === "lti.get_data.response") {
   
                  const splitContent = event.data.value.split('|')
                  
                  let result = {};
            
                  for (let i = 0; i < splitContent.length; i += 2) {
                        result[splitContent[i]] = splitContent[i + 1];
                  }
   
                  window.removeEventListener('message', handleResponse);

                  resolve({
                     key: "headers",
                     value: {
                        skipInterceptor: true,
                        [contextData.session_storage_key]: result[contextData.session_storage_key],
                        [contextData.refresh_token_storage_key]: result[contextData.refresh_token_storage_key]
                     }
                  })
   
               if (event.data.error) {
                  reject(new Error(`${event.data.error.code} - ${event.data.error.message}`))
                  }
               }
            })
         }
      }
   )
}

axios.interceptors.response.use(
   async (response) => {
       // Return successful responses - do nothing
       return response;
   },
   async (error) => {
      // TODO: Catch other 401 and 403 errors and either force a relaunch of the app or poke the user to do it.
       // Checks for 401 SessionExpiredError to attempt a refresh and retry
       if (error.response && error.response.status === 401 && error.response.data.type === "SessionExpiredError") {
         // Try to refresh session token
            try {
               const contextData = window.contextData
               const headerConfig = await refreshSessionConfig()

               return await axios.post(
                  `${contextData.tool_domain}/session/refresh`, 
                  null, 
                  headerConfig
               ).then(
                  (response) => {
                     // 3rd-party cookie policies require an alternate flow to store the new tokens, LMS's like Canvas require this
                     // Cookies are just applied by themselves without this mess
                     if (contextData.storage_target !== "cookie") {
                        let platformOrigin = new URL(contextData.oidc_auth_domain).origin
                        let parent = window.parent || window.opener
                        const storageTarget = contextData.storage_target
                        let targetFrame = contextData.storage_target === "_parent" ? parent : parent.frames[storageTarget];
         
                        const sessionMessageId = crypto.randomUUID()
                        targetFrame.postMessage({
                           "subject": "lti.put_data",
                           "message_id": sessionMessageId,
                           "key": contextData.session_storage_key,
                           "value": `${contextData.session_storage_key}|${response.data.new_session_id}|exp|${response.data.session_expiration}|${contextData.refresh_token_storage_key}|${response.data.refresh_token}`
                        }, platformOrigin)
                     }
                     // Retry the axios call after session refresh
                     return axios(error.config);
                  }
               ).catch(
                  () => Promise.reject(new Error("Session Expired, failed to refresh", {cause: "SessionRefreshError"}))
               )

            } catch (refreshError) {
               return Promise.reject(refreshError);
            }
         }
         // If the error is not a 401, reject it as is
         return Promise.reject(error);
   }
   );

app.mount("#app")


