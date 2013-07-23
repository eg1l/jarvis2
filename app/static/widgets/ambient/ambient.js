var jarvis = jarvis || angular.module('jarvis', []);

jarvis.controller('AmbientCtrl', ['$scope',
  function ($scope) {
    'use strict';

    $scope.$on('ambient', function (ev, body) {
      angular.extend($scope, body);
    });

  }
]);