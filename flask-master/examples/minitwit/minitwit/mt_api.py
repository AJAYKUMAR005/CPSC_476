import minitwit 
import click
from flask import Flask

app = Flask('minitwit')

def populate_db():
    """Re-populates the database with test data"""
    db = get_db()
    with app.open_resource('population.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('populatedb')
def populatedb_command():
    """Inputs data in database tables."""
    populate_db()
    print('Database population is completed.')
    click.echo('database population is completed')

if __name__ == '__main__':
    app.run()
