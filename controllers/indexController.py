from flask import Flask, render_template

def indexController():
    return render_template(
        'index.html'
        )