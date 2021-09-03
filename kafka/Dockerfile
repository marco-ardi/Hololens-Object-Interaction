FROM openjdk:8-jre-alpine

ENV PATH /opt/kafka/bin:$PATH
ENV KAFKA_DIR "/opt/kafka"
ARG KAFKA_VERSION="2.13-2.7.0"

RUN apk update && apk add --no-cache bash gcompat

# Installing Kafka
# ADD will automatically extract the file
ADD setup/kafka_${KAFKA_VERSION}.tgz /opt

# Create Sym Link 
RUN ln -s /opt/kafka_${KAFKA_VERSION} ${KAFKA_DIR} 

# Copy All conf here
ADD conf/* ${KAFKA_DIR}/config/

WORKDIR ${KAFKA_DIR}
