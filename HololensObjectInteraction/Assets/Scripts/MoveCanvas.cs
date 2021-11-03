using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace HoloToolkit.Unity
{
    /// <summary>
    /// A Tagalong that stays at a fixed distance from the camera and always
    /// seeks to stay on the edge or inside a sphere that is straight in front of the camera.
    /// </summary>
    public class MoveCanvas : MonoBehaviour
    {
        // how far to stay away fromt he center
        public float offsetRadius = 0.1f;
        public float distanceToHead = 0.8f;

        public Camera FirstPersonCamera;

        // This is a value between 0 and 1 where
        // 0 object never moves
        // 1 object jumps to targetPosition immediately
        // 0.5 e.g. object is placed in the middle between current and targetPosition every frame
        // you can play around with this in the Inspector
        [Range(0, 1)]
        public float smoothFactor = 0.5f;

        void Start()
        {
            InvokeRepeating("FollowCamera", 0.0f, 0.04f);   //will update 25 times per second
        }

        private void FollowCamera()
        {
            // make the UI always face towards the camera
            transform.rotation = FirstPersonCamera.transform.rotation;

            var cameraCenter = FirstPersonCamera.transform.position + FirstPersonCamera.transform.forward * distanceToHead;
            var currentPos = transform.position;
            // in which direction from the center?
            var direction = currentPos - cameraCenter;
            // target is in the same direction but offsetRadius
            // from the center
            var targetPosition = cameraCenter + direction.normalized * offsetRadius;
            // finally interpolate towards this position
            transform.position = Vector3.Lerp(currentPos, targetPosition, smoothFactor);
        }
    }
}