workflow "Check on push" {
  resolves = ["Style check"]
  on = "push"
}

action "Style check" {
  uses = "bulv1ne/python-style-check@v0.3"
}
