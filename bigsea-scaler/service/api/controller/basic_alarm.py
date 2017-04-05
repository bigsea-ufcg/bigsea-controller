from utils.logger import configure_logging, Log

# TODO: documentation


class Basic_Alarm:

    # TODO: Think about these constants placements
    PROGRESS_METRIC_NAME = "spark.job_progress"
    ELAPSED_TIME_METRIC_NAME = 'spark.elapsed_time'

    def __init__(self, actuator, metric_source, trigger_down, trigger_up, min_cap, max_cap, actuation_size, metric_rounding):
        # TODO: Check parameters
        self.metric_source = metric_source
        self.actuator = actuator
        self.trigger_down = trigger_down
        self.trigger_up = trigger_up
        self.min_cap = min_cap
        self.max_cap = max_cap
        self.actuation_size = actuation_size
        self.metric_rounding = metric_rounding

        self.logger = Log("basic.alarm.log", "controller.log")
        configure_logging()

    def check_application_state(self, application_id, instances, expected_time):
        # TODO: Check parameters
        self.logger.log("Getting progress")
        job_progress = float(self.metric_source.get_most_recent_value(Basic_Alarm.PROGRESS_METRIC_NAME,
                                                                {"application_id":application_id}))
        job_progress = round(job_progress, self.metric_rounding)
        self.logger.log("Getting time progress")
        time_progress = float(self.metric_source.get_most_recent_value(Basic_Alarm.ELAPSED_TIME_METRIC_NAME,
                                                                 {"application_id":application_id}))
        time_progress = round(time_progress, self.metric_rounding)
        self.logger.log("Progress:%d|Time progress:%d" % (job_progress, time_progress))

        diff = job_progress - 100 * time_progress / expected_time

        if diff > 0 and diff >= self.trigger_down:
            self.logger.log("Scaling down")
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = cap - self.actuation_size
            cap_instances = {instance:new_cap for instance in instances}

            self.actuator.adjust_resources(cap_instances)
        elif diff < 0 and abs(diff) >= self.trigger_up:
            self.logger.log("Scaling up")
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = cap + self.actuation_size
            cap_instances = {instance:new_cap for instance in instances}

            self.actuator.adjust_resources(cap_instances)
