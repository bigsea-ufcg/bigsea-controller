from utils.logger import Log, configure_logging
import datetime

class Generic_Alarm:

    ERROR_METRIC_NAME = "application-progress.error"

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

        self.logger = Log("generic.alarm.log", "controller.log")
        configure_logging()
        
        self.last_progress_error_timestamp = datetime.datetime.strptime("0001-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')

    def check_application_state(self, application_id, instances):
        # TODO: Check parameters
        try:
            self.logger.log("Getting progress error")
            progress_error_timestamp, progress_error = self._get_progress_error(application_id)
            
            self.logger.log("Progress error-[%s]-%f" % (str(progress_error_timestamp), progress_error))

            if self._check_measurements_are_new(progress_error_timestamp):
                self._scale_down(progress_error, instances)
                self._scale_up(progress_error, instances)
                    
                self.last_progress_error_timestamp = progress_error_timestamp
            else:
                self.logger.log("Could not acquire more recent metrics")
        except Exception:
            # TODO: Check exception type
            self.logger.log("Could not get metrics")
            return

    def _scale_down(self, progress_error, instances):
        if progress_error > 0 and progress_error >= self.trigger_down:
            self.logger.log("Scaling down")
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = max(cap - self.actuation_size, self.min_cap)
            cap_instances = {instance:new_cap for instance in instances}
            
            self.actuator.adjust_resources(cap_instances)
            
    def _scale_up(self, progress_error, instances):
        if progress_error < 0 and abs(progress_error) >= self.trigger_up:
            self.logger.log("Scaling up")
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = min(cap + self.actuation_size, self.max_cap)
            cap_instances = {instance:new_cap for instance in instances}
    
            self.actuator.adjust_resources(cap_instances)
    
    def _get_progress_error(self, application_id):
        progress_error_measurement = self.metric_source.get_most_recent_value(Generic_Alarm.ERROR_METRIC_NAME,
                                                                {"application_id":application_id})
        progress_error_timestamp = progress_error_measurement[0]
        progress_error = progress_error_measurement[1]
        progress_error = round(progress_error, self.metric_rounding)
        return progress_error_timestamp, progress_error

    def _check_measurements_are_new(self, progress_error_timestamp):
        return self.last_progress_error_timestamp < progress_error_timestamp
