# LAB BUDDY

An agent for the monitoring of the safety of lab users when lone working.

## The problem

I am a mechanical engineer and often have to conduct experiments in my lab.
The lab is a dangerous place. There are hazardous chemicals which I use in my experiments (anti-freeze, oil, gasoline and other fuels, etc...), and the experimental equipment itself can be dangerous under certain cirmcumstances (an engine which spins at high speeds). As such, a policy of no lone working is in place, meaning there is always someone else in the lab with me while I conduct my experiment. This also means that if I want to be in my lab then I need someone else available to be my "lab buddy", which is not always the case. If there is no one available then I cannot conduct any experiments.

## The solution

In the case where no one else is availble, and it is imperative to conduct experiments, then LAB BUDDY is a potential solution. It is an agentic system designed to constantly assess the safety of the lab user when lone working.

### How it works

Every 10 seconds (the check duration can be changed) BUDDY takes a picture of the lab space using the computer camera, then using Gemini as the background LLM, it assesses whether the lab user appears safe. If the user is safe then a chime is played (this can be disabled) and another safety check will be conducted later. If the user is deemed unsafe, or if the user cannot be seen or the image is inconclusive, then BUDDY will ask for verbal confimation of safety using the computer's microphone. Once again, using Gemini as the background LLM, the user's safety will be assessed, and if deemed safe then a chime is played and another check is conducted later. If at this point the user is deemed unsafe, either through verbal indication or simply due to inconclusive visual and verbal checks, then BUDDY will activate an audio alarm on the computer as well as send an email to the relevant person (such as a supervisor or lab manager) detailing the reason for the emergency email.

## The disclaimer

This was something I created for a hackathon, and in reality will never use in my lab work. This is because even an automated alarm system, which is what BUDDY is, cannot fully ensure my safety in my lab and it in no way can replace the knowledge and help my real lab buddy (a person) provides.