using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class StartStopRecording : MonoBehaviour
{
    public GameObject textmesh;
    private TextMeshPro label;

    void Start()
    {
        //textmesh = GetComponent<TextMeshPro>();
        label = textmesh.GetComponent<TextMeshPro>();
    }
    public void ChangeState()
    {
        HandTracking.canRun = !HandTracking.canRun;
        if (HandTracking.canRun)
        {
            label.text = "Stop";
        }
        else
        {
            label.text = "Start";
        }
        Debug.Log("canRun=" + HandTracking.canRun);
        Debug.Log("label=" + label.text);
    }

    public void CheckState()
    {
        HandTracking.canRun = false;
        if (HandTracking.canRun)
        {
            label.text = "Stop";
        }
        else
        {
            label.text = "Start";
        }
        Debug.Log("canRun=" + HandTracking.canRun);
        Debug.Log("label=" + label.text);
    }
}
