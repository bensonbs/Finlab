# We start from the wuuker/python-talib image
FROM wuuker/python-talib

# Update and install git, pip, gcc and python3-dev
RUN apt-get update && apt-get install -y git python3-pip gcc python3-dev && \
    pip3 install --upgrade pip

# Set environment variables
ENV HOME /home/jovyan
ENV NB_PASS ""
ENV FINLAB_API_KEY "" 
ENV OPENAI_API_KEY ""

# Clone your repository
RUN git clone https://github.com/bensonbs/Finlab ${HOME}/Finlab && \
    pip3 install -r ${HOME}/Finlab/requirement.txt && \
    pip3 install jupyterlab

# Jupyter will run on port 8888, expose this port
EXPOSE 8888

# The command to run when this image starts up:
CMD ["bash", "-c", "streamlit run ${HOME}/Finlab/main.py & jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.password=$NB_PASS"]