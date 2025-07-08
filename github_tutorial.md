# GitHub and Git Tutorial for Jacob

Welcome, Jacob! This guide will walk you through the basics of Git and GitHub. Understanding these concepts will help you work on the `stonesoup` project and collaborate effectively with your colleague, Macon.

## 1. Core Concepts: Git & GitHub

### What is Git?

Think of Git as a program on your MacBook that lets you save "snapshots" of your code at different points in time. It's a **Version Control System**. This is useful because:

*   **History**: You can look back at the entire history of changes.
*   **Safety**: If you make a mistake, you can easily go back to a previous working version.
*   **Collaboration**: It helps multiple people work on the same project without overwriting each other's work.

### What is GitHub?

GitHub is a website that hosts Git repositories. Think of it as a central cloud storage for your code projects. Your local `stonesoup` folder is a **local repository**, and the one on `github.com` is the **remote repository**.

Key terms:

*   **Repository (Repo)**: A project's folder. The `stonesoup` folder is your local repo.
*   **Commit**: A saved snapshot of your changes. Each commit has a unique ID and a message describing the changes.
*   **Branch**: A parallel version of the repository. This allows you to work on new features without affecting the main codebase (often called the `main` or `master` branch).
*   **Clone**: What we just did. It's downloading a full copy of a remote repository to your computer.

## 2. How You and Macon Will Stay in Sync

Since both you and Macon are working on the `stonesoup` project, you need a way to share changes. This is done by synchronizing your local repositories with the central remote repository on GitHub.

Here are the two most important commands you'll use:

*   `git pull`: This **downloads** the latest changes from the GitHub repository to your local machine. If Macon has made changes and pushed them to GitHub, you will use `git pull` to get those changes.
*   `git push`: This **uploads** your committed changes from your local machine to the GitHub repository. After you've made and saved your changes locally, you'll use `git push` to share them with Macon.

## 3. Your Daily Workflow

Here is a simple, repeatable workflow you can follow when you work on the project.

**Step 1: Get the Latest Changes**

Before you start working, always run this command in your terminal from the `/Users/jacobgoldman/Documents/Starling/stonesoup` directory:

```bash
git pull
```

This ensures you have the most up-to-date version of the project, including any changes Macon has made.

**Step 2: Make Your Changes**

Work on the files as you normally would. Add new code, fix bugs, etc.

**Step 3: Save Your Changes (Commit)**

Once you're happy with your changes, you need to save them to your local repository. This is a two-step process.

First, you tell Git which files you want to save. To add all your changes, run:

```bash
git add .
```

Second, you create the commit (the snapshot) with a descriptive message:

```bash
git commit -m "A short description of the changes I made"
```

**Step 4: Share Your Changes with Macon**

Now that your changes are saved locally, you need to upload them to GitHub so Macon can see them. Run:

```bash
git push
```

And that's it! Macon will then be able to `git pull` your changes.

## Next Steps

1.  I recommend you read through this file again to familiarize yourself with the concepts.
2.  We should configure Git with your name and email. This is important because it will attach your identity to the commits you create.
3.  I can walk you through a practice run of the `pull -> change -> add -> commit -> push` cycle.

Let me know how you'd like to proceed!
