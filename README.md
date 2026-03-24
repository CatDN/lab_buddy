# LAB BUDDY

An agent for the monitoring of the safety of lab users when lone working.

## The problem

I am a mechanical engineer and often have to conduct experiments in my lab.
The lab is a dangerous place. There are hazardous chemicals which I use in my experiments (anti-freeze, oil, gasoline and other fuels, etc...), and the experimental equipment itself can be dangerous under certain cirmcumstances (an engine which spins at high speeds). As such, a policy of no lone working is in place, meaning there is always someone else in the lab with me while I conduct my experiment. This also means that if I want to be in my lab then I need someone else available to be my "lab buddy", which is not always the case. If there is no one available then I cannot conduct any experiments.

## The solution

In the case where no one else is availble, and it is imperative to conduct experiments, then LAB BUDDY is a potential solution. It is an agentic system designed to constantly assess the safety of the lab user when lone working.

BUDDY continuously assesses user safety through both video capturea as well as real time audio transcription. If at any point the users safety is in question, then BUDDY (using the underlying gemini model) will send an email to the relevant person, such as a lab manager or PI, containing both the latest camera frame as well as the reson for the assessment.



### Version 2 (current)

BUDDY Version 2 improves on the main issues outlined in Version 1. BUDDY is no longer overly reliant on gemini and also performs safety checks continuously.

- Camera checks are first conducted using YOLO26 for checking whether a person is in frame, whether they are moving and whether they are sumpled over. This is done continuously through video streaming.

- Speech to text transcription is performed using the ElevenLabs API in real time.

- Gemini is only used to assess user safety through both the video feed as well as the audio transcript and then contact the relevant person. 



### Version 1

Version 1 of BUDDY was simple:

- every `x` seconds BUDDY would check the camera (by taking a single photo) using gemini and the camera tool

- if gemini thought no person was present in the frame or if their safety was unceratin then it would ask for verbal confirmation by reccording 8 seconds of audio (voice reccording tool)

- if there was no verbal confirmation or if gemini determined the user sounded in distress, then it would sound an alarm (alarm tool) as well as contact a relevant person through email and describing the reson for the email (email tool)

- if gemini thought everything was fine at any point then nothing would happen and another check would be conducted `x` seconds later

BUDDY essentially relied on gemini to make all the resoning as well as use all the tools necessary to ascertain the user safety and then sound the alarm and contact the relevant person. This way, a person could lone work in a lab because if anything happened then there would be an automatic way to contact someone.

There were 2 main issues with this version:

1. All the checks and tool callings involved calling upon the gemini API, and as I am currently in the free tier which is limited to 20 requests per day, BUDDY could only run approximately 1 check per API key before using up the resquest quota

2. The safety assessment is not continuous. Every `x` seconds safety was assessed, meaning nothing would happen between those seconds and no context on the user status was available to the agent.





