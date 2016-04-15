/**
 * Created by nandre on 4/13/16.
 */


//myApp.directive('myDirective', function() {});
//myApp.factory('myService', function() {});


var hours = Array.apply(null, Array(24)).map(function (_, i) {return i;});
var days = Array.apply(null, Array(7)).map(function (_, i) {return i;});
var weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

var scheduleApp = angular.module('scheduleApp',[]).controller('ScheduleCtrl',[ '$scope', '$http' , '$window', function ($scope, $http, $window) {
    $scope.hours = hours;
    $scope.days = days;
    $scope.weekdays = weekdays;
    $scope.selections = [];
    $scope.lengths = [1,2,3];
    $scope.scheduled_slots = [];
    $scope.alternating = false;

    $scope.cellClick = function(day, hour) {
    	var array_cell = day*24 + hour;
    	//console.log('array cell ' + array_cell);
      var i, a = $scope.selections;
      
      for(i = 0; i < a.length; ++i) {
      	if (array_cell == a[i].cell) {
        	$scope.selections.splice(i,1);
          return;
        }
      }
        for (i = array_cell; i < array_cell + $scope.length; i++) {
            if ($scope.scheduled_slots.indexOf(i) > -1)
                return;
        }
      $scope.selections.push({
      weekday: weekdays[day],
      day: day,
      cell: array_cell,
      hour: hour
      });
    };

    $scope.calculateEnd = function(hour) {
      return (parseInt(hour) + parseInt($scope.length)) % 24;
    };

    $scope.clearSelections = function() {
    	$scope.selections = [];
    };
    $scope.deleteSelection = function(ind) {
    	$scope.selections.splice(ind,1);
    };
    $scope.whatColor = function(day, hour) {
    	var current_cell = day*24 + hour;
        var i, cell, end;
        var a = $scope.selections;
        if ($scope.scheduled_slots.indexOf(current_cell) > -1) {
            return 3;
        }

          for(i = 0; i < a.length; ++i) {
            cell = a[i].cell;
            if (cell == current_cell) {
                return 1;
            }
          }
          for(i = 0; i < a.length; ++i) {
          cell = parseInt(a[i].cell);
          end = (cell + parseInt($scope.length)) % (7 * 24);
          if (end < cell && (current_cell > cell || current_cell < end)) {
              return 2;
          }
          if (current_cell > cell && current_cell < end) {
              return 2;
          }
      }
    };
    
    $scope.submit = function() {
        data = {
            alternating : $scope.alternating,
            length : $scope.length,
            slots : $scope.selections
        };
        
        //json_data = JSON.stringify(data);
        $http({
            method:'POST',
            url:'/scheduleapi',
            headers: {
                'Content-Type' : 'application/json'
            },
            data : data
        }).then(function successCallback(response){
            $window.location.href = '/';
        }, function errorCallback(response) {
            console.error("Schedule API Call returned " + response.status + " during POST with a response " + response.data);
        });
    };
    var init = function() {
        $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http({
            method:'GET',
            url: '/scheduleapi'
        }).then(function successCallback(response) {
            var r = response.data;
            $scope.scheduled_slots = r.scheduled_slots;
            $scope.selections = r.user_slots;

            if (r.user_slots.length > 0) {
                $scope.length = $scope.lengths[r.user_slots[0].length - 1];
                $scope.alternating = r.user_slots[0].alternating;
            } else {
                $scope.length = $scope.lengths[0];
            }

        }, function errorCallback(response){
            console.error("Schedule API Call returned " + response.status + " during GET with a response " + response.data);
        });
    };
    init();
}]);