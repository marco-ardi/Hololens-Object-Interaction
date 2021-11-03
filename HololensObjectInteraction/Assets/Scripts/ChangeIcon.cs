using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Microsoft.MixedReality.Toolkit.UI
{
    public class ChangeIcon : MonoBehaviour
    {
        // Start is called before the first frame update
        public Texture2D stopT;
        public Texture2D startT;
        public Texture2D outputTexture;
        public Sprite stopS;
        public Sprite startS;
        public Sprite outputSprite;
        public GameObject obj;
        ButtonConfigHelper conf;
        public void ChangeIt()
        {
            if (HandTracking.canRun)
            {
                outputTexture = stopT;
                outputSprite = stopS;
            }
            else
            {
                outputTexture = startT;
                outputSprite = startS;
            }
            //img.SetActive(true);
            conf = obj.GetComponent<ButtonConfigHelper>();
            conf.SetSpriteIcon(outputSprite);
            conf.SetQuadIcon(outputTexture);
            //Debug.Log("mesh texture is=" + outputTexture);
            //img.GetComponent<MeshRenderer>().material.mainTexture = outputTexture;
        }
    }
}
