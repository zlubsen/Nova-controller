import unittest

from protocol import *

class ProtocolBuilderTest(unittest.TestCase):

    def testNoModuleProvided(self):
        builder = createCommand()
        try:
            builder.build()
            self.fail()
        except AssertionError:
            self.assertTrue(True)

    def testIncorrectModuleProvided(self):
        builder = createCommand()
        builder.setModule("not_existing_module").setAsset("servo1").setOperation("set_degree").setArgs(['90'])
        try:
            builder.build()
            self.fail()
        except AssertionError:
            self.assertTrue(True)

    def testNoAssetProvided(self):
        builder = createCommand()
        cmd = builder.setModule("nova").setOperation("set_mode").setArgs(['1'])
        try:
            builder.build()
            self.fail()
        except AssertionError:
            self.assertTrue(True)

    def testIncorrectAssetProvided(self):
        builder = createCommand()
        builder.setModule("nova").setAsset("non_existing_asset").setOperation("set_degree").setArgs(['90'])
        try:
            builder.build()
            self.fail()
        except AssertionError:
            self.assertTrue(True)

    def testDefaultToModuleAsset(self):
        expected = ['0','0','1','1','2']

        builder = createCommand()
        cmd = builder.setModule("nova").setOperation("set_mode").setArgs(['2']).build()
        self.assertListEqual(cmd, expected)

    def testNoOperationProvided(self):
        builder = createCommand()
        cmd = builder.setModule("nova").setAsset("module").setArgs(['1'])
        try:
            builder.build()
            self.fail()
        except AssertionError:
            self.assertTrue(True)

    def testIncorrectOperationProvided(self):
        builder = createCommand()
        builder.setModule("nova").setAsset("module").setOperation("non_existing_operation").setArgs(['90'])
        try:
            builder.build()
            self.fail()
        except AssertionError:
            self.assertTrue(True)

    def testSetMode(self):
        expected = ['0','0','1','1','3']
        builder = createCommand()
        cmd = builder.setModule("nova").setAsset("module").setOperation("set_mode").setModeArg("external_input").build()
        self.assertListEqual(cmd, expected)

    def testExternalInputMoveCommand(self):
        expected = ['3','5','2','1','90']
        builder = createCommand()
        cmd = builder.setModule("external_input").setAsset("servo5").setOperation("set_degree").setArgs(['90']).build()
        self.assertListEqual(cmd, expected)

    def testTrackObjectSetCoordinates(self):
        args = ['90','90']
        expected = ['5','0','1','2','90','90']

        builder = createCommand()
        cmd = builder.setModule("track_object").setAsset("module").setOperation("set_coordinates").setArgs(args).build()
        self.assertListEqual(cmd, expected)

    def testSetPIDTuning(self):
        args = ['500','400','0']
        expected = ['4','1','3','3','500','400','0']

        builder = createCommand()
        cmd = builder.setModule("keep_distance").setAsset("pid").setOperation("set_tuning").setArgs(args).build()
        self.assertListEqual(cmd, expected)

class ProtocolReaderTest(unittest.TestCase):

    def testReadServoStatusCommand(self):
        received = ['0','1','1','1','90']
        expected = ['nova','servo1','get_degree',['90']]

        reader = NovaProtocolCommandReader()
        cmd = reader.readCommand(received)
        self.assertListEqual(cmd, expected)

    def testReadTrackObjectAckCommand(self):
        received = ['5','0','2','0']
        expected = ['track_object', 'module', 'ack_coordinates', []]

        reader = NovaProtocolCommandReader()
        cmd = reader.readCommand(received)
        self.assertListEqual(cmd, expected)

    def testGetPIDTuning(self):
        received = ['4','1','4','3','500','400','0']
        expected = ['keep_distance', 'pid', 'get_tuning', ['500','400','0']]

        reader = NovaProtocolCommandReader()
        cmd = reader.readCommand(received)
        self.assertListEqual(cmd, expected)

class ProtocolUtilTest(unittest.TestCase):

    def testListPIDNodes(self):
        expected = {
            "keep_distance" : ["pid"],
            "track_object" : ["pid_x", "pid_y"]
        }
        found = mapPIDNodes()

        self.fail()
        #self.assertTrue(expected == found)

if __name__ == "__main__":
    unittest.main()
