# nwb_eyetracking

This repository contains python code to explore and analyze the dataset provided by @rutishauserlab for the paper titled "Multimodal single-neuron, intracranial EEG, and fMRI brain responses during movie watching in human patients" [Link to paper](https://doi.org/10.1038/s41597-024-03029-1). 
[Link to Dataset](https://dandiarchive.org/dandiset/000623). [Link to original github](https://github.com/rutishauserlab/bmovie-release-NWB-BIDS)
## Table of Contents
- [Introduction](#introduction)
- [Structure](#Structure)
- [Plots](#Plots)

## Introduction
This analyses only focuses on nwb exploration for eyetracking. After the eytracking data is analyzed the next step is to align the spikes accordingly.
Note that data from patient id 53 had calibaration issues and has as such been ignored in this analysis. 

## Structure
This file explores the structure of the dataset from high level to the basic keys and raw data. Section 1 and 2 focus on data from the processing module only (eyetracking and behaviour modules). While Section 3 explores trials as default but the input can be changed to explore the other modules.

## Plots 
This script processes the dataset to extract and visualize key eye-tracking metrics. The primary goal is to quantify cognitive effort and memory retrieval by examining specific markers like Fixation Duration, Pupil Size, and Saccade dynamics. Comparison of Correct versus Incorrect trials to demonstrate that the increased fixation duration observed in the recognition phase is not simply a reaction to looking at static images.

## Extract Saccde and Fixation
### Sample Event Stream (sub-CS41)

| Event Type | Start Time (s) | End Time (s) |
| :--- | :--- | :--- |
| Saccade | 0.302 | 0.314 |
| Fixation | 0.314 | 0.430 |
| Saccade | 0.430 | 0.470 |
| Fixation | 0.470 | 0.634 |

### Dataset Summary (Event Counts)

This summary shows the total number of gaze events processed for each patient across both experimental conditions:

| Patient ID | Encoding Events | Recognition Events |
| :--- | :--- | :--- |
| **sub-CS41** | 3,154 | 2,518 |
| **sub-CS42** | 3,642 | 4,074 |
| **sub-CS43** | 2,958 | 2,336 |
| **sub-CS47** | 3,182 | 3,099 |
| **sub-CS48** | 3,330 | 2,717 |
| **sub-CS49** | 3,261 | 2,520 |
| **sub-CS51** | 3,130 | 4,092 |
| **sub-CS54** | 4,086 | 3,484 |
| **sub-CS55** | 2,752 | 3,457 |
| **sub-CS56** | 4,545 | 4,302 |
| **sub-CS57** | 3,329 | 3,503 |
| **sub-CS62** | 4,164 | 2,845 |
## Paired t test - for fixation duration
This script performs a paired t-test on fixation durations to compare 
Encoding and Recognition sessions across all patients.

We use a paired t-test because we are comparing the same subjects under 
two different conditions. The analysis calculates the mean duration for 
each task per patient and finds the individual differences. 

By comparing the average of these differences against the variation (noise), 
the test maps the result onto a T-distribution curve. The P-value represents 
the area under this curve.
### 1. Results Summary

