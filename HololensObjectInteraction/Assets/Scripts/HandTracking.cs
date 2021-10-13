using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;


using Microsoft;
using Microsoft.MixedReality.Toolkit.Utilities;
using Microsoft.MixedReality.Toolkit.Input;
using Microsoft.MixedReality.Toolkit;
using System.Globalization;

public class HandTracking : MonoBehaviour
{

    MixedRealityPose pose;
    string msgToSend;
    public TCPTestClient client;
    PhotoCaptureExample PhotoCap;

    //does this in order to prevent comma in floating point numbers, it causes errors in .csv files
    public NumberFormatInfo nfi;


    void Start()
    {
        nfi = new NumberFormatInfo();
        nfi.NumberDecimalSeparator = ".";

        msgToSend = "";
        //should set frame rate to 30fps
        Application.targetFrameRate = 30;
        PhotoCap = this.gameObject.GetComponent<PhotoCaptureExample>();
        client = this.gameObject.GetComponent<TCPTestClient>();
        PhotoCap.setClient(client);
        InvokeRepeating("Execute", 2f, 4.0f);   //wait 2s, then run Execute() once per 3 seconds
    }

    public void GetHandData(Handedness yourHand, out MixedRealityPose pose)
    {
        if (HandJointUtils.TryGetJointPose(TrackedHandJoint.ThumbTip, yourHand, out pose))
        {
            msgToSend += (pose.Position.x).ToString(nfi) + " ";     //adding nfi in ToString() in order to write point separated number instead of comma separated ones
            msgToSend += (pose.Position.y).ToString(nfi) + " ";
            msgToSend += (pose.Position.z).ToString(nfi) + " ";
        }
        else
        {
            msgToSend += "-1 -1 -1 ";
        }

        if (HandJointUtils.TryGetJointPose(TrackedHandJoint.IndexTip, yourHand, out pose))
        {
            msgToSend += (pose.Position.x).ToString(nfi) + " ";
            msgToSend += (pose.Position.y).ToString(nfi) + " ";
            msgToSend += (pose.Position.z).ToString(nfi) + " ";
        }
        else
        {
            msgToSend += "-1 -1 -1 ";
        }

        if (HandJointUtils.TryGetJointPose(TrackedHandJoint.MiddleTip, yourHand, out pose))
        {
            msgToSend += (pose.Position.x).ToString(nfi) + " ";
            msgToSend += (pose.Position.y).ToString(nfi) + " ";
            msgToSend += (pose.Position.z).ToString(nfi) + " ";
        }
        else
        {
            msgToSend += "-1 -1 -1 ";
        }

        if (HandJointUtils.TryGetJointPose(TrackedHandJoint.RingTip, yourHand, out pose))
        {
            msgToSend += (pose.Position.x).ToString(nfi) + " ";
            msgToSend += (pose.Position.y).ToString(nfi) + " ";
            msgToSend += (pose.Position.z).ToString(nfi) + " ";
        }
        else
        {
            msgToSend += "-1 -1 -1 ";
        }

        if (HandJointUtils.TryGetJointPose(TrackedHandJoint.PinkyTip, yourHand, out pose))
        {
            msgToSend += (pose.Position.x).ToString(nfi) + " ";
            msgToSend += (pose.Position.y).ToString(nfi) + " ";
            msgToSend += (pose.Position.z).ToString(nfi) + " ";
        }
        else
        {
            msgToSend += "-1 -1 -1 ";
        }
    }

    public void GetEyeGaze()
    {
        Vector3 gazePos = CoreServices.InputSystem.EyeGazeProvider.GazeOrigin + CoreServices.InputSystem.EyeGazeProvider.GazeDirection.normalized;
        Debug.Log("gazePos=" + gazePos.x + gazePos.y + gazePos.z);
        msgToSend += (gazePos.x).ToString(nfi) + " ";
        msgToSend += (gazePos.y).ToString(nfi) + " ";
        msgToSend += (gazePos.z).ToString(nfi) + " ";
    }


    void Execute()
    {
        Debug.Log("Provo ad inviare");
        long ldap = DateTimeOffset.Now.ToUnixTimeMilliseconds() + 60 * 60 * 2;
        string str = "0.###########";     //does this in order to prevent scientific notation
        str = ldap.ToString();
        msgToSend += str + " ";
        GetEyeGaze();
        GetHandData(Handedness.Left, out pose);
        GetHandData(Handedness.Right, out pose);
        //msgToSend += "\n";
        Debug.Log(msgToSend);
        client.SendMsg(msgToSend);
        PhotoCap.TakeImage();
        msgToSend = "";
    }
}
