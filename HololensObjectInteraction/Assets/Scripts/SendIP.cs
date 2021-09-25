using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class SendIP : MonoBehaviour
{
    public InputField myField;

    public void Submit()
    {
        //Debug.Log(myField.text);
        TCPTestClient.IP = myField.text;
        SceneManager.LoadScene("SampleScene");
    }
}
