---
title: Using Nix with Dockerfiles
slug: using-nix-with-dockerfiles
author: h0ffmann
published: true
summary: Explaining the benefits of pairing Nix with Dockerfiles for building container images, with a basic example.
publish_date: 2023-04-23 # Mimic the date from the image
tags:
  - Nix
  - Docker
  - DevOps
  - Build
---

[Nix](https://nixos.org/) is a powerful cross-platform package management tool. The benefits of Nix are far reaching, but one big benefit is that once you adopt Nix, you can get a consistent environment across development (on both Linux and Mac), CI, and production.

I've been [using Nix for many years](/) and recently started building Docker images using a Dockerfile paired with Nix. This post will explain the benefits of this approach along with a basic example to show how it looks and feels.

> **Sorry, this is not a Nix introduction post.** You don't need to know how to use Nix to read this post, but I am also not going to explain basic Nix concepts or introduce the Nix language. If you do not know Nix, you can still read this post and use it to determine if Nix is interesting for you to learn.

## Dockerfiles Are Easy, Why Nix?

Dockerfiles are quite easy -- you just chain together shell commands -- so understandably there is some hesitation to introduce a tool like Nix into the mix. The practical reason is that if you use Nix, you'll get always-working environments on local machines, CI, Docker, and more for free; you have little to no duplicated effort.

A typical, non-Nix approach is to have a separate effort for local development, CI, and Docker image building. This often leads to drift and inconsistencies. Using Nix provides a single source of truth for your dependencies and environment setup.

# (More content would follow here...)
