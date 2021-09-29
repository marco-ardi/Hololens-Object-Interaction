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
            Debug.Log($"LaunchUri: Launching {"http://" + TCPTestClient.IP + ":5601"}");

#if WINDOWS_UWP
            UnityEngine.WSA.Application.InvokeOnUIThread(async () =>
            {
                bool result = await global::Windows.System.Launcher.LaunchUriAsync(new System.Uri("http://www.google.com/"));
                //bool result = await global::Windows.System.Launcher.LaunchUriAsync(new System.Uri("http://" + TCPTestClient.IP + ":5601"));
                if (!result)
                {
                    Debug.LogError("Launching URI failed to launch.");
                }
            }, false);
#else
            //Application.OpenURL("http://www.google.com/");
            Application.OpenURL("http://" + TCPTestClient.IP + ":5601");
#endif
        }
    }
}
