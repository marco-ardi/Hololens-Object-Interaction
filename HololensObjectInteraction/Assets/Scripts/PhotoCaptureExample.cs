using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using System.Linq;
using UnityEngine.Windows.WebCam;
using System.IO;
using Microsoft.MixedReality.Toolkit;
using Microsoft.MixedReality.Toolkit.Input;
using Microsoft.MixedReality.Toolkit.Utilities;
using System.Globalization;

public class PhotoCaptureExample : MonoBehaviour
{
    private PhotoCapture photoCaptureObject = null;
    private Texture2D targetTexture = null;
    private Resolution cameraResolution;

    private TCPTestClient client = null;



    // Use this for initialization
    public void Start()
    {
        cameraResolution = UnityEngine.Windows.WebCam.VideoCapture.SupportedResolutions.OrderByDescending((res) => res.width * res.height).First();
        //cameraResolution = PhotoCapture.SupportedResolutions.OrderByDescending((res) => res.width * res.height).First();
        //cameraResolution = new Resolution { width = 1280, height = 720, refreshRate = 0 };
        //debugText.text = cameraResolution.width.ToString() + " " + cameraResolution.height.ToString();
        targetTexture = new Texture2D(cameraResolution.width, cameraResolution.height);  //default hololens resolution is 3904x2196, it's too much
        //targetTexture = new Texture2D(1280, 720);
        // targetTexture = new Texture2D(480, 270);
        // InputManager.Instance.PushFallbackInputHandler(gameObject);
    }


    public void setClient(TCPTestClient _client)
    {
        this.client = _client;

    }

    void OnStoppedPhotoMode(PhotoCapture.PhotoCaptureResult result)
    {
        photoCaptureObject.Dispose();
        photoCaptureObject = null;
    }


    void OnCapturedPhotoToMemory(PhotoCapture.PhotoCaptureResult result, PhotoCaptureFrame photoCaptureFrame)
    {
        photoCaptureFrame.UploadImageDataToTexture(targetTexture);
        //Debug.Log("Invio l'immagine al server.");
        //byte[] bytes = targetTexture.EncodeToPNG();
        byte[] bytes = targetTexture.EncodeToJPG();
        client.SendImage(bytes);
        photoCaptureObject.StopPhotoModeAsync(OnStoppedPhotoMode);
    }

    public void TakeImage()
    {
        if (this.client != null)
        {
            PhotoCapture.CreateAsync(false, delegate (PhotoCapture captureObject)   //true -> Holograms, false -> No Holograms
            {
                //Debug.Log("Entered in TakeImage()");
                photoCaptureObject = captureObject;
                CameraParameters cameraParameters = new CameraParameters();
                cameraParameters.hologramOpacity = 0.9f;
                cameraParameters.cameraResolutionWidth = cameraResolution.width;
                cameraParameters.cameraResolutionHeight = cameraResolution.height;
                cameraParameters.pixelFormat = CapturePixelFormat.BGRA32;
                photoCaptureObject.StartPhotoModeAsync(cameraParameters, delegate (PhotoCapture.PhotoCaptureResult result)
                {
                    photoCaptureObject.TakePhotoAsync(OnCapturedPhotoToMemory);
                });
            });
        }
    }
}