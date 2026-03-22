# LAB BUDDY

An agent for the monitoring of the safety of lab users when lone working.

## The problem

I am a mechanical engineer and often have to conduct experiments in my lab.
The lab is a dangerous place. There are hazardous chemicals which I use in my experiments (anti-freeze, oil, gasoline and other fuels, etc...), and the experimental equipment itself can be dangerous under certain cirmcumstances (an engine which spins at high speeds). As such, a policy of no lone working is in place, meaning there is always someone else in the lab with me while I conduct my experiment. This also means that if I want to be in my lab then I need someone else available to be my "lab buddy", which is not always the case. If there is no one available then I cannot conduct any experiments.

## The solution

In the case where no one else is availble, and it is imperative to conduct experiments, then LAB BUDDY is a potential solution. It is an agentic system designed to constantly assess the safety of the lab user when lone working.

### How it works

BUDDY continuously assesses user safety through both video capturea as well as real time audio transcription. If at any point the users safety is in question, then BUDDY (using the underlying gemini model) will send an email to the relevant person, such as a lab manager or PI, containing both the latest camera frame as well as the reson for the assessment.

