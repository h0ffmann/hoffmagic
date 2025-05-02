---
title: hello world!
title_pt: olá mundo!
slug: hello-world
author: h0ffmann
published: true
summary: How to take raw text and turn it into a Markdown file with YAML frontmatter.
tags:
  - test
---

This post explains how to take raw text and turn it into a Markdown file that includes YAML frontmatter. It's useful for content management systems or static site generators that read metadata from files. We'll cover the basics.

## First Steps

You need a text editor. Then, you follow these steps:

1.  Start the file with three dashes (`---`).
2.  Add metadata using `key: value` pairs (like `title:` and `slug:`). Ensure lists (like `tags`) use the `-` prefix.
3.  End the metadata section with three more dashes (`---`).
4.  Write your normal **Markdown** content below the closing dashes!

# Welcome to hoffmagic

Hello and welcome to hoffmagic, a blog dedicated to exploring ideas at the intersection of philosophy, technology, and human experience.

## What to Expect

On this blog, you'll find:

- **Thoughtful essays** on topics ranging from ancient philosophy to cutting-edge technology
- **Practical guides** for living more intentionally in the digital age
- **Book reviews** and recommendations for further exploration
- **Reflections** on current events through a philosophical lens

I'm excited to embark on this journey of ideas with you. Please feel free to engage with the content through comments or reach out directly through the [contact page](/contact).

Thank you for visiting, and I hope you'll find something here that sparks your curiosity or challenges your thinking.

### Monte Carlo pi calculus - code snipped sample
```python
import random
import math

def calculate_pi(num_samples=1000000):
    """
    Calculate π using the Monte Carlo method.
    
    This method works by:
    1. Generating random points in a square with side length 2
    2. Counting how many points fall inside a circle with radius 1
    3. Using the ratio to estimate π
    
    Args:
        num_samples: Number of random points to generate
        
    Returns:
        An approximation of π
    """
    points_inside_circle = 0
    
    for _ in range(num_samples):
        # Generate random point in square with corners at (-1,-1) and (1,1)
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        
        # Check if point is inside circle of radius 1
        # (A point is inside if x² + y² ≤ 1)
        if x**2 + y**2 <= 1:
            points_inside_circle += 1
    
    # π ≈ 4 * (points inside circle / total points)
    pi_approximation = 4 * points_inside_circle / num_samples
    return pi_approximation

# Example usage
if __name__ == "__main__":
    # Try with different sample sizes
    samples = [1000, 10000, 100000, 1000000]
    
    print("Monte Carlo π Approximation")
    print("--------------------------")
    print(f"{'Samples':<10} {'Approximation':<15} {'Error':<10}")
    print("--------------------------")
    
    for n in samples:
        pi_approx = calculate_pi(n)
        error = abs(pi_approx - math.pi)
        print(f"{n:<10} {pi_approx:<15.10f} {error:<10.10f}")
    
    print("--------------------------")
    print(f"Actual π: {math.pi:.10f}")
```

<div class="embed-gist" data-gist-url="https://gist.github.com/louismullie/3769218.js">Loading Gist...</div>

