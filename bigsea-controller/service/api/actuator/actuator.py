# Copyright (c) 2017 LSD - UFCG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import abstractmethod
from abc import ABCMeta

# TODO: documentation


class Actuator:
    __metaclass__ = ABCMeta

    @abstractmethod
    def prepare_environment(self, vm_data):
        pass

    @abstractmethod
    def adjust_resources(self, vm_data):
        pass

    @abstractmethod
    def get_allocated_resources(self, vm_id):
        pass
