var jarvis = jarvis || angular.module('jarvis', []);

jarvis.controller('LeafCtrl', ['$scope',
  function ($scope) {
    'use strict';

    var gauge = null;
    var initGauge = function (element, battery) {
      gauge = new JustGage({
          id: element.id,
          title: ' ',
          min: 0,
          max: battery.capacity,
          value: battery.remaining,
          label: 'prosent',
          showMinMax: true,
          valueFontColor: '#FFFFFF',
          gaugeColor: '#38A6CB',
          labelColor: '#FFFFFF',
          gaugeWidthScale: 0.7,
          levelColors: ['#FF0000','#FAD328','#09C000'],
          showInnerShadow: true,
          startAnimationTime: 2000,
          refreshAnimationTime: 2000,
      });
    };

    $scope.$on('leaf', function (ev, body) {
      angular.extend($scope, body);
      if (gauge === null) {
        var element = document.querySelector('#gauge');
        if (element !== null) {
          initGauge(element, body.battery);
        }
      } else {
        // Round to nearest 10
//        gauge.refresh((Math.round((100/12*getRandomInt(0,12))/10))*10);
        gauge.refresh(body.battery.remaining);
      }
    });
  }
]);
