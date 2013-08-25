var jarvis = jarvis || angular.module('jarvis', []);

jarvis.controller('LeafCtrl', ['$scope',
  function ($scope) {
    'use strict';

    var gauges = {
      battery: null,
    };

    var opts = {
      lines: 12,
      angle: 0.07,
      lineWidth: 0.3,
      pointer: {
        length: 0.85,
        strokeWidth: 0.045,
        color: '#ffffff'
      },
      percentColors: [[0,"#FF0000"],[.5,"#FAD328"],[1,"#09C000"]],
      strokeColor: '#38A6CB'
    };

    var updateGauge = function (gauge, body) {
      if (gauges[gauge] === null) {
        var target = document.querySelector('#leaf #' + gauge);
        var textField = document.querySelector('#leaf #' + gauge + '-text');
        gauges[gauge] = new Gauge(target).setOptions(opts);
        gauges[gauge].setTextField(textField);
        gauges[gauge].maxValue = body.battery.capacity;
        gauge.animationSpeed = 100;
      }
      gauges[gauge].set(body.battery.remaining);
    };

    $scope.$on('leaf', function (ev, body) {
      updateGauge('battery', body);
      angular.extend($scope, body);
    });
  }
]);
