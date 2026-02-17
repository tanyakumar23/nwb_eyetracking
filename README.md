# nwb_eyetracking

This repository contains python code to explore and analyze the dataset provided by @rutishauserlab for the paper titled "Multimodal single-neuron, intracranial EEG, and fMRI brain responses during movie watching in human patients" [Link to paper](https://doi.org/10.1038/s41597-024-03029-1). 

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

## Paired t test
This script performs a paired t-test on fixation durations to compare 
Encoding and Recognition sessions across all patients.

We use a paired t-test because we are comparing the same subjects under 
two different conditions. The analysis calculates the mean duration for 
each task per patient and finds the individual differences. 

By comparing the average of these differences against the variation (noise), 
the test maps the result onto a T-distribution curve. The P-value represents 
the area under this curve.
### 1. Results Summary

| Metric | Value |
| :--- | :--- |
| **Encoding Mean** | 0.3967s |
| **Recognition Mean** | 0.3972s |
| **T-statistic** | -0.0223 |
| **P-value** | 0.9826 |
