# FROM public.ecr.aws/lambda/python:3.12
# RUN dnf install python-devel postgresql-devel rpm-build
# # Copy function code
# COPY ./api ${LAMBDA_TASK_ROOT}
# # Install the function's dependencies using file requirements.txt
# # from your project folder.
# COPY ./api/requirements.txt .
# RUN pip install -r requirements.txt
# # RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" -U -no-cache-dir
# # Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
# CMD [ "api.handler" ]

# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.12 as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY ./api ${FUNCTION_DIR}

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

# Install the function's dependencies
RUN pip install --target ${FUNCTION_DIR} awslambdaric
RUN pip install -r ${FUNCTION_DIR}/requirements.txt --target ${FUNCTION_DIR}

# Use a slim version of the base Python image to reduce the final image size
FROM python:3.12-slim

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "api.handler" ]