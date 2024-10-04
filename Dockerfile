FROM python:3.12

# Create a group and user
RUN useradd -m -U app

# Create the /app directory
RUN mkdir /app

# Change the owner of the /app directory
RUN chown -R app:app /app

# Use the app user
USER app

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY --chown=app:app . /app

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
RUN /home/app/.local/bin/poetry install

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
CMD ["/home/app/.local/bin/poetry", "run", "uwsgi", "--yaml", "uwsgi.yaml"]
