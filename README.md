# JCI-Splunk-addon / Johnson Control Smart Building
A none-official JCI app for Splunk to get audit data from your Johnson Control Smart-Building app to your Splunk enviroment using REST API.
Current version - 1.0.0

# Intsalling the app
To Install the Splunk add-on straight to your Splunk deployment simply follow these few simple steps:
  - Download the file named: 'TA-jci-logs-fetcher_1_0_0_export.tgz'.
  - follow this link to the Splunk documentation regarding installing new add-ons in various ways: https://docs.splunk.com/Documentation/AddOns/released/Overview/Installingadd-ons
  - Installing using CLI:
      1. Upload the .tgz file to your Splunk server under location: "/tmp/" ; On a distributed SE set-up use your Splunk Manager deployment server for this task.
      2. Unzip the .tgz file to the desited location - "tar xvzf splunk_package_name.tgz -C $SPLUNKHOME/etc/apps"; For distributed SE use this path - "$SPLUNKHOME/etc/deployment-apps".
      3. For single instance users -
you should now see your new Splunk app ready for use in your Splunk GUI.
      4. For distributed SE -
          * navigate to your Splunk Manager deployment GUI.
          * Under 'Settings' click 'Forwarder Management'.
          * In the search box type the name of the app - 'TA-jci-logs-fetcher'.
          * Click 'Edit'.
          * Using the '+' button assign the app to all of your desired Splunk server classes (make sure to check 'Restart Splunkd').
           * Wait for the Splunk deployments associated with this server class to load back up, you shall now see the app available in the associated deployment's GUI.

# Setting up a new data input:
When clicking on creating a new data input for the app there are several parameters the user needs to fill out.

- Client_Id - The client id is a special string representing your user - this is used to generate a bearer token for fetching data.
- Client_Secret - Coupled with your client id, this special string is a super sensitive key that completes the authentication and grants the permission for the app to receive the bearer token.
- Host - Provide your hostname to be used as the base_url in the HTTP requests.
- IMS_org - This is a string that specifies which organization is associated with the credentials you have provided (client_id & secret).
- Run_time - This feature enables you the option to schedule a time condition for the program to be executed; if you wish to fetch data only at a night/morning/noon - you can do so by entering your desired time in HH:MM:SS format. To turn/leave this feature off you can simply enter '0'.
- time_delta - This feature is a dependent of the Run_time feature. If you have enabled and set a Run_time condition, you can also define a time delta for your run time condition to make sure it is cought in between the your time condition and the Splunk running interval the app.
Of course you could run the app every 60 seconds, but in order to save resources, I have decided to implement a time_delta feature to allow the user (you) to set larger Splunk intervals for this app and still use the Run_time condition.
- Fetch_for_past + Time_unit - set your desired look-back range; e.g. - 5 minutes / 3 hours / 10 days etc.
- Verify SSL - This checkbox allows you to control wether you would like to include an SSL verification with every HTTP request made by this app.
- Proxy - In any case you need to use a proxy server, simply configure your proxy under 'Configuration' tab in the app's main page.

# Contact me
Found a bug? want to request a new feature? missing data? API updated?
You can contact me at: amitngithub23@gmail.com
