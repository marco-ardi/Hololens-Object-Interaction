using System;
using UnityEngine;

namespace Microsoft.MixedReality.Toolkit.Examples.Demos
{
    public class OpenBrowserOnClick : MonoBehaviour
    {
        /// <summary>
        /// Launch a UWP slate app. In most cases, your experience can continue running while the
        /// launched app renders on top.
        /// </summary>
        /// <param name="uri">Url of the web page or app to launch. See https://docs.microsoft.com/en-us/windows/uwp/launch-resume/launch-default-app
        /// for more information about the protocols that can be used when launching apps.</param>
        public void Open()
        {
            Debug.Log($"LaunchUri: Launching {"http://" + TCPTestClient.IP + ":5601/app/dashboards#/view/c1a2b170-2c55-11ec-9356-8f87c0fef758?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!f%2Cvalue%3A3000)%2Ctime%3A(from%3A'2021-10-13T15%3A30%3A54.493Z'%2Cto%3Anow))"}");

#if WINDOWS_UWP
            UnityEngine.WSA.Application.InvokeOnUIThread(async () =>
            {
                //bool result = await global::Windows.System.Launcher.LaunchUriAsync(new System.Uri("http://www.google.com/"));
                bool result = await global::Windows.System.Launcher.LaunchUriAsync(new System.Uri("http://" + TCPTestClient.IP + ":5601/app/dashboards#/view/c1a2b170-2c55-11ec-9356-8f87c0fef758?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!f%2Cvalue%3A3000)%2Ctime%3A(from%3A'2021-10-13T15%3A30%3A54.493Z'%2Cto%3Anow))"));
                if (!result)
                {
                    Debug.LogError("Launching URI failed to launch.");
                }
            }, false);
#else
            //Application.OpenURL("http://www.google.com/");
            Application.OpenURL("http://" + TCPTestClient.IP + ":5601/app/dashboards#/view/c1a2b170-2c55-11ec-9356-8f87c0fef758?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!f%2Cvalue%3A3000)%2Ctime%3A(from%3A'2021-10-13T15%3A30%3A54.493Z'%2Cto%3Anow))");
#endif
        }
    }
}
